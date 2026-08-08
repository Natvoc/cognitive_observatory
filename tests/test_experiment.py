import json
import subprocess
import sys
from pathlib import Path

from core.experiments import load_experiment

_YAML = """
name: hidden_variable_test
seed: 7
steps: 50

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
  - type: predictive
    name: agent_2_predictive
"""


def _write_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "experiment.yaml"
    config_path.write_text(_YAML, encoding="utf-8")
    return config_path


def test_run_produces_traces_of_expected_length(tmp_path: Path) -> None:
    experiment = load_experiment(_write_config(tmp_path))
    result = experiment.run()

    assert len(result.ground_truth_trace) == 50
    assert len(result.observation_trace) == 50
    assert set(result.beliefs) == {"agent_0_reactive", "agent_2_predictive"}
    assert len(result.beliefs["agent_0_reactive"]) == 50
    assert len(result.beliefs["agent_2_predictive"]) == 50


def test_run_is_deterministic_given_same_seed(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)

    result_a = load_experiment(config_path).run()
    result_b = load_experiment(config_path).run()

    assert result_a.ground_truth_trace == result_b.ground_truth_trace
    assert result_a.observation_trace == result_b.observation_trace
    assert result_a.beliefs == result_b.beliefs


def test_save_writes_expected_json_files(tmp_path: Path) -> None:
    experiment = load_experiment(_write_config(tmp_path))
    result = experiment.run()

    output_dir = tmp_path / "output"
    result.save(output_dir)

    for filename in ("config.json", "ground_truth.json", "observations.json", "beliefs.json"):
        assert (output_dir / filename).exists()

    ground_truth = json.loads((output_dir / "ground_truth.json").read_text(encoding="utf-8"))
    assert len(ground_truth) == 50
    assert "hidden_state" not in ground_truth[0].get("variables", {})


def test_cli_run_persists_json_under_experiments_dir(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)

    result = subprocess.run(
        [sys.executable, "-m", "core.cli", "run", str(config_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    run_dirs = list((tmp_path / "experiments").glob("*_hidden_variable_test_7"))
    assert len(run_dirs) == 1
    output_dir = run_dirs[0]
    for filename in ("config.json", "ground_truth.json", "observations.json", "beliefs.json"):
        assert (output_dir / filename).exists()


def test_cli_run_same_seed_produces_byte_identical_json(tmp_path: Path) -> None:
    for run_dir_name in ("run_a", "run_b"):
        run_dir = tmp_path / run_dir_name
        run_dir.mkdir()
        (run_dir / "experiment.yaml").write_text(_YAML, encoding="utf-8")
        subprocess.run(
            [sys.executable, "-m", "core.cli", "run", "experiment.yaml"],
            cwd=run_dir,
            capture_output=True,
            text=True,
            check=True,
        )

    dir_a = next((tmp_path / "run_a" / "experiments").glob("*"))
    dir_b = next((tmp_path / "run_b" / "experiments").glob("*"))

    for filename in ("ground_truth.json", "observations.json", "beliefs.json"):
        assert (dir_a / filename).read_bytes() == (dir_b / filename).read_bytes()
