import subprocess
import sys
import warnings
from pathlib import Path

import pytest

from core import cli

_MINIMAL_YAML = """
name: cli_report_failure_test
seed: 3
steps: 20

world:
  hidden_state: A
  initial_temperature: 20.0
  initial_light: 0.5
  initial_position: [0, 0]
  temperature_noise_std: 0.1
  light_noise_std: 0.05
  light_drift: 0.01

sensor:
  type: noisy
  noise_std: 0.05

agents:
  - type: reactive
    name: agent_0_reactive
"""


def test_cli_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "core.cli", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "cognitive-observatory" in result.stdout


def test_run_succeeds_even_if_report_generation_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "experiment.yaml"
    config_path.write_text(_MINIMAL_YAML, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    def _boom(output_dir: Path) -> Path:
        raise RuntimeError("simulated report failure")

    monkeypatch.setattr(cli, "generate_report", _boom)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        exit_code = cli.main(["run", str(config_path)])

    assert exit_code == 0
    assert any("report.html generation failed" in str(w.message) for w in caught)

    run_dirs = list((tmp_path / "experiments").glob("*_cli_report_failure_test_3"))
    assert len(run_dirs) == 1
    output_dir = run_dirs[0]
    for filename in (
        "config.json",
        "ground_truth.json",
        "observations.json",
        "beliefs.json",
        "metrics.json",
        "divergence.json",
    ):
        assert (output_dir / filename).exists()
    assert not (output_dir / "report.html").exists()
