from pathlib import Path

from core.reporting import generate_report


def _write_run(output_dir: Path) -> None:
    output_dir.mkdir(parents=True)
    (output_dir / "config.json").write_text(
        '{"name": "test_run", "seed": 1, "steps": 3}', encoding="utf-8"
    )
    (output_dir / "ground_truth.json").write_text(
        '[{"causal_state": {"hidden_state": "A"}}, '
        '{"causal_state": {"hidden_state": "A"}}, '
        '{"causal_state": {"hidden_state": "A"}}]',
        encoding="utf-8",
    )
    (output_dir / "beliefs.json").write_text(
        '{"agent_0": ['
        '{"predicted_hidden_state": "A", "confidence": 1.0}, '
        '{"predicted_hidden_state": "A", "confidence": 1.0}, '
        '{"predicted_hidden_state": "B", "confidence": 1.0}]}',
        encoding="utf-8",
    )
    (output_dir / "metrics.json").write_text('{"agent_0": [0.0, 0.0, 1.0]}', encoding="utf-8")
    (output_dir / "divergence.json").write_text('{"agent_0": [0.0, 0.0, 1.4]}', encoding="utf-8")


def test_generate_report_writes_self_contained_html(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    _write_run(output_dir)

    report_path = generate_report(output_dir)

    assert report_path == output_dir / "report.html"
    html_text = report_path.read_text(encoding="utf-8")
    assert "<html" in html_text
    assert "test_run" in html_text
    assert "agent_0" in html_text
    assert "<script" not in html_text
    assert "http://" not in html_text and "https://" not in html_text


def test_generate_report_shows_correct_final_window_accuracy(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    _write_run(output_dir)

    report_path = generate_report(output_dir)
    html_text = report_path.read_text(encoding="utf-8")

    # 2 correct out of 3 steps (A, A, B vs true A, A, A)
    assert "0.6667" in html_text


def test_generate_report_tolerates_missing_divergence_file(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    _write_run(output_dir)
    (output_dir / "divergence.json").unlink()

    report_path = generate_report(output_dir)

    assert report_path.exists()
    assert "agent_0" in report_path.read_text(encoding="utf-8")
