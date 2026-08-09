"""report.html generator (roadmap Fase 5.2): a self-contained, readable
summary of one persisted experiment run.

Deliberately decoupled from Experiment/ExperimentResult - this only
reads the JSON files a run already left behind (config.json,
ground_truth.json, beliefs.json, metrics.json, divergence.json), so it
can be pointed at any past run directory without touching the runner
itself. Static only (inline SVG, no JS) - interactivity is the Fase 6
dashboard's job, not this.
"""

import html
import json
from pathlib import Path
from typing import Any


def generate_report(output_dir: Path) -> Path:
    config = _read_json(output_dir / "config.json", default={})
    ground_truth = _read_json(output_dir / "ground_truth.json", default=[])
    beliefs = _read_json(output_dir / "beliefs.json", default={})
    metrics = _read_json(output_dir / "metrics.json", default={})
    divergence = _read_json(output_dir / "divergence.json", default={})

    truths = [gt.get("causal_state", {}).get("hidden_state") for gt in ground_truth]
    agent_names = sorted(beliefs)

    sections = "".join(
        _agent_section(
            name,
            beliefs.get(name, []),
            metrics.get(name, []),
            divergence.get(name, []),
            truths,
        )
        for name in agent_names
    )

    html_doc = _PAGE_TEMPLATE.format(
        title=html.escape(str(config.get("name", output_dir.name))),
        seed=html.escape(str(config.get("seed", "?"))),
        steps=html.escape(str(config.get("steps", len(truths)))),
        config_json=html.escape(json.dumps(config, indent=2)),
        sections=sections,
    )

    report_path = output_dir / "report.html"
    report_path.write_text(html_doc, encoding="utf-8")
    return report_path


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _agent_section(
    name: str,
    beliefs: list[dict[str, Any]],
    errors: list[float],
    divergences: list[float],
    truths: list[str | None],
) -> str:
    steps = len(beliefs)
    window = min(1000, steps) or 1
    correct = [
        b.get("predicted_hidden_state") == t for b, t in zip(beliefs[-window:], truths[-window:])
    ]
    accuracy = sum(correct) / len(correct) if correct else 0.0
    error_tail = errors[-window:]
    avg_error = sum(error_tail) / len(error_tail) if error_tail else 0.0
    divergence_tail = divergences[-window:]
    avg_divergence = sum(divergence_tail) / len(divergence_tail) if divergence_tail else 0.0

    return _AGENT_TEMPLATE.format(
        name=html.escape(name),
        accuracy=f"{accuracy:.4f}",
        avg_error=f"{avg_error:.4f}",
        avg_divergence=f"{avg_divergence:.4f}",
        window=window,
        error_sparkline=_sparkline(errors),
        divergence_sparkline=_sparkline(divergences),
    )


def _sparkline(values: list[float], width: int = 560, height: int = 80) -> str:
    if not values:
        return "<p class='muted'>(sin datos)</p>"

    sampled = _subsample(values, max_points=300)
    lo, hi = min(sampled), max(sampled)
    span = (hi - lo) or 1.0
    n = len(sampled)

    points = " ".join(
        f"{(i / (n - 1) if n > 1 else 0) * width:.1f},"
        f"{height - ((v - lo) / span) * height:.1f}"
        for i, v in enumerate(sampled)
    )
    return (
        f"<svg viewBox='0 0 {width} {height}' class='sparkline'>"
        f"<polyline points='{points}' fill='none' stroke='currentColor' stroke-width='1.5' />"
        f"</svg>"
        f"<div class='sparkline-range'><span>min {lo:.4f}</span><span>max {hi:.4f}</span></div>"
    )


def _subsample(values: list[float], max_points: int) -> list[float]:
    if len(values) <= max_points:
        return values
    step = len(values) / max_points
    return [values[int(i * step)] for i in range(max_points)]


_PAGE_TEMPLATE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>{title} - Cognitive Observatory report</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{
    font-family: system-ui, sans-serif;
    max-width: 860px;
    margin: 2rem auto;
    padding: 0 1rem;
    line-height: 1.5;
  }}
  h1 {{ margin-bottom: 0.2rem; }}
  .meta {{ color: #666; margin-bottom: 2rem; }}
  .agent {{
    border: 1px solid #8884;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 1.5rem;
  }}
  .agent h2 {{ margin-top: 0; font-size: 1.1rem; }}
  .stats {{ display: flex; gap: 2rem; margin: 0.75rem 0 1rem; flex-wrap: wrap; }}
  .stat .value {{ font-size: 1.4rem; font-weight: 600; }}
  .stat .label {{ font-size: 0.8rem; color: #666; }}
  .chart-label {{ font-size: 0.8rem; color: #666; margin-top: 0.75rem; }}
  .sparkline {{ width: 100%; height: 80px; color: #2563eb; }}
  .sparkline-range {{
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #666;
  }}
  .muted {{ color: #666; font-size: 0.85rem; }}
  details summary {{ cursor: pointer; color: #666; }}
  pre {{
    background: #8881;
    padding: 0.75rem;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 0.8rem;
  }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="meta">seed={seed} &middot; steps={steps}</p>
{sections}
<details>
<summary>config.json</summary>
<pre>{config_json}</pre>
</details>
</body>
</html>
"""

_AGENT_TEMPLATE = """<section class="agent">
<h2>{name}</h2>
<div class="stats">
  <div class="stat">
    <div class="value">{accuracy}</div>
    <div class="label">accuracy (últimos {window})</div>
  </div>
  <div class="stat">
    <div class="value">{avg_error}</div>
    <div class="label">prediction_error prom. (últimos {window})</div>
  </div>
  <div class="stat">
    <div class="value">{avg_divergence}</div>
    <div class="label">reality-model divergence prom. (últimos {window})</div>
  </div>
</div>
<div class="chart-label">prediction_error a lo largo del run</div>
{error_sparkline}
<div class="chart-label">reality-model divergence a lo largo del run</div>
{divergence_sparkline}
</section>
"""
