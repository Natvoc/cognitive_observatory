"""Fase 7.2 - analisis del barrido: lee las corridas que dejo
scripts/batch_runner.py (Fase 7.1) bajo experiments/, arma una tabla
arquitectura x sensor_noise de reality-model divergence (spec §7.1),
identifica que arquitectura gana en cada nivel de ruido y en promedio, y
genera un reporte HTML autocontenido con un heatmap SVG a mano (mismo
criterio sin dependencias que core/reporting) mostrando la interaccion
entre ambos parametros.

Usa la divergencia promediada sobre los PRIMEROS `EARLY_WINDOW` steps de
cada corrida, no los ultimos: con memoria/belief bayesiano, cualquier
cantidad de ruido gaussiano termina promediandose dado suficiente
tiempo/capacidad, asi que en estado estacionario (ultimos steps) casi
todas las arquitecturas no-reactivas empatan en divergencia ~0 sin
importar el nivel de ruido - eso ya no diferencia nada. La diferencia
real entre arquitecturas esta en que tan rapido llegan ahi, no en si
llegan.
"""

import csv
import html
import json
from datetime import date
from pathlib import Path
from typing import Any

SEED = 42
EARLY_WINDOW = 100


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _discover_batch_runs(experiments_dir: Path) -> list[Path]:
    runs = []
    for entry in sorted(experiments_dir.iterdir()):
        config_path = entry / "config.json"
        if not entry.is_dir() or not config_path.exists():
            continue
        config = _read_json(config_path)
        is_batch_run = str(config.get("name", "")).startswith("batch_sensor_noise_")
        if config.get("seed") == SEED and is_batch_run:
            runs.append(entry)
    return runs


def _early_avg_divergence(run_dir: Path, agent: str) -> float | None:
    divergence = _read_json(run_dir / "divergence.json")
    series: list[float] | None = divergence.get(agent)
    if not series:
        return None
    head = series[:EARLY_WINDOW]
    return sum(head) / len(head)


def _collect_results(run_dirs: list[Path]) -> tuple[dict[float, dict[str, float]], list[str]]:
    results: dict[float, dict[str, float]] = {}
    agent_names: set[str] = set()
    for run_dir in run_dirs:
        config = _read_json(run_dir / "config.json")
        noise_std = config["sensor_noise_std"]
        agents = config["agents"]
        agent_names.update(agents)
        results[noise_std] = {}
        for agent in agents:
            divergence = _early_avg_divergence(run_dir, agent)
            if divergence is not None:
                results[noise_std][agent] = divergence
    return results, sorted(agent_names)


def _print_table(
    architectures: list[str], noise_levels: list[float], results: dict[float, dict[str, float]]
) -> None:
    header = f"{'architecture':>30} | " + " | ".join(f"noise={n:.2f}" for n in noise_levels)
    print(header)
    for arch in architectures:
        cells = [results[n].get(arch) for n in noise_levels]
        cell_strs = [f"{c:.4f}" if c is not None else "-" for c in cells]
        print(f"{arch:>30} | " + " | ".join(f"{s:>10}" for s in cell_strs))


def _winners(
    architectures: list[str], noise_levels: list[float], results: dict[float, dict[str, float]]
) -> tuple[dict[float, str], str, dict[str, float]]:
    winners_per_noise = {}
    for n in noise_levels:
        available = [a for a in architectures if a in results[n]]
        winners_per_noise[n] = min(available, key=lambda a: results[n][a])

    overall_avg = {}
    for arch in architectures:
        values = [results[n][arch] for n in noise_levels if arch in results[n]]
        if values:
            overall_avg[arch] = sum(values) / len(values)
    overall_winner = min(overall_avg, key=lambda a: overall_avg[a])

    return winners_per_noise, overall_winner, overall_avg


def _save_csv(
    experiments_dir: Path,
    architectures: list[str],
    noise_levels: list[float],
    results: dict[float, dict[str, float]],
) -> Path:
    csv_path = experiments_dir / f"{date.today().isoformat()}_batch_analysis_summary.csv"
    fieldnames = ["architecture", *[f"noise_{n}" for n in noise_levels]]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for arch in architectures:
            row: dict[str, Any] = {"architecture": arch}
            for n in noise_levels:
                row[f"noise_{n}"] = results[n].get(arch)
            writer.writerow(row)
    return csv_path


def _color_for(value: float, lo: float, hi: float) -> str:
    span = (hi - lo) or 1.0
    t = max(0.0, min(1.0, (value - lo) / span))
    # green (low divergence, good) -> red (high divergence, bad)
    r = int(22 + t * (220 - 22))
    g = int(163 - t * (163 - 38))
    b = int(74 - t * (74 - 38))
    return f"rgb({r},{g},{b})"


def _heatmap_svg(
    architectures: list[str], noise_levels: list[float], results: dict[float, dict[str, float]]
) -> str:
    cell_w, cell_h = 110, 40
    label_w, label_h = 220, 30
    width = label_w + cell_w * len(noise_levels)
    height = label_h + cell_h * len(architectures)

    all_values = [v for n in noise_levels for v in results[n].values()]
    lo, hi = (min(all_values), max(all_values)) if all_values else (0.0, 1.0)

    parts = [f"<svg viewBox='0 0 {width} {height}' class='heatmap'>"]
    for col, n in enumerate(noise_levels):
        x = label_w + col * cell_w + cell_w / 2
        parts.append(f"<text x='{x:.0f}' y='20' text-anchor='middle'>noise={n:.2f}</text>")
    for row, arch in enumerate(architectures):
        y = label_h + row * cell_h
        parts.append(f"<text x='0' y='{y + cell_h / 2 + 4:.0f}'>{html.escape(arch)}</text>")
        for col, n in enumerate(noise_levels):
            x = label_w + col * cell_w
            value = results[n].get(arch)
            if value is None:
                parts.append(
                    f"<rect x='{x}' y='{y}' width='{cell_w - 4}' height='{cell_h - 4}' "
                    f"fill='#8882' />"
                )
                continue
            color = _color_for(value, lo, hi)
            parts.append(
                f"<rect x='{x}' y='{y}' width='{cell_w - 4}' height='{cell_h - 4}' "
                f"fill='{color}' />"
            )
            parts.append(
                f"<text x='{x + (cell_w - 4) / 2:.0f}' y='{y + cell_h / 2 + 4:.0f}' "
                f"text-anchor='middle' fill='#111' font-size='11'>{value:.3f}</text>"
            )
    parts.append("</svg>")
    return "".join(parts)


_PAGE_TEMPLATE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Batch analysis - Cognitive Observatory</title>
<style>
  body {{
    font-family: system-ui, sans-serif;
    max-width: 900px;
    margin: 2rem auto;
    padding: 0 1rem;
  }}
  h1 {{ margin-bottom: 0.2rem; }}
  .meta {{ color: #666; margin-bottom: 1.5rem; }}
  .heatmap text {{ font-size: 12px; fill: #333; }}
  .winners {{ margin-top: 1.5rem; }}
  .winners li {{ margin-bottom: 0.25rem; }}
</style>
</head>
<body>
<h1>Fase 7.2 - Batch analysis</h1>
<p class="meta">
  reality-model divergence promedio en los primeros {window} steps
  (velocidad de convergencia), seed={seed}
</p>
{heatmap}
<div class="winners">
  <h2>Ganador por nivel de ruido</h2>
  <ul>{winners_list}</ul>
  <h2>Ganador global (promedio entre niveles de ruido)</h2>
  <p>{overall_winner} (avg divergence={overall_divergence})</p>
</div>
</body>
</html>
"""


def _save_html_report(
    experiments_dir: Path,
    architectures: list[str],
    noise_levels: list[float],
    results: dict[float, dict[str, float]],
    winners_per_noise: dict[float, str],
    overall_winner: str,
    overall_avg: dict[str, float],
) -> Path:
    winners_list = "".join(
        f"<li>noise={n:.2f}: <strong>{html.escape(winners_per_noise[n])}</strong> "
        f"(divergence={results[n][winners_per_noise[n]]:.4f})</li>"
        for n in noise_levels
    )
    html_doc = _PAGE_TEMPLATE.format(
        window=EARLY_WINDOW,
        seed=SEED,
        heatmap=_heatmap_svg(architectures, noise_levels, results),
        winners_list=winners_list,
        overall_winner=html.escape(overall_winner),
        overall_divergence=f"{overall_avg[overall_winner]:.4f}",
    )
    html_path = experiments_dir / f"{date.today().isoformat()}_batch_analysis.html"
    html_path.write_text(html_doc, encoding="utf-8")
    return html_path


def main() -> None:
    experiments_dir = Path("experiments")
    run_dirs = _discover_batch_runs(experiments_dir)
    if not run_dirs:
        print(
            "no batch_sensor_noise_* runs found under experiments/ - "
            "run scripts/batch_runner.py first."
        )
        return

    results, architectures = _collect_results(run_dirs)
    noise_levels = sorted(results)

    print(f"reality-model divergence promedio, primeros {EARLY_WINDOW} steps:\n")
    _print_table(architectures, noise_levels, results)

    winners_per_noise, overall_winner, overall_avg = _winners(architectures, noise_levels, results)
    print("\nGanador por nivel de ruido (menor reality-model divergence temprana):")
    for n in noise_levels:
        winner = winners_per_noise[n]
        print(f"  noise={n:.2f}: {winner} (divergence={results[n][winner]:.4f})")
    print(
        f"\nGanador global (promedio entre niveles de ruido): {overall_winner} "
        f"(avg divergence={overall_avg[overall_winner]:.4f})"
    )

    csv_path = _save_csv(experiments_dir, architectures, noise_levels, results)
    print(f"\nsummary csv -> {csv_path}")

    html_path = _save_html_report(
        experiments_dir,
        architectures,
        noise_levels,
        results,
        winners_per_noise,
        overall_winner,
        overall_avg,
    )
    print(f"report -> {html_path}")


if __name__ == "__main__":
    main()
