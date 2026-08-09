from pathlib import Path

import pytest

from dashboard.api.runs import RunNotFoundError, list_runs, load_run


def _write_run(
    experiments_dir: Path, run_id: str, *, name: str = "test_run", seed: int = 1
) -> None:
    run_dir = experiments_dir / run_id
    run_dir.mkdir(parents=True)
    (run_dir / "config.json").write_text(
        f'{{"name": "{name}", "seed": {seed}, "steps": 3}}', encoding="utf-8"
    )
    (run_dir / "ground_truth.json").write_text("[1, 2, 3]", encoding="utf-8")
    (run_dir / "beliefs.json").write_text('{"agent_0": []}', encoding="utf-8")


def test_list_runs_on_missing_directory_returns_empty(tmp_path: Path) -> None:
    assert list_runs(tmp_path / "does_not_exist") == []


def test_list_runs_skips_directories_without_config(tmp_path: Path) -> None:
    (tmp_path / "not_a_run").mkdir()
    assert list_runs(tmp_path) == []


def test_list_runs_returns_summary_from_config(tmp_path: Path) -> None:
    _write_run(tmp_path, "2026-01-01_hidden_variable_42", name="hidden_variable", seed=42)

    runs = list_runs(tmp_path)

    assert len(runs) == 1
    assert runs[0].run_id == "2026-01-01_hidden_variable_42"
    assert runs[0].name == "hidden_variable"
    assert runs[0].seed == 42
    assert runs[0].steps == 3


def test_load_run_returns_all_available_files(tmp_path: Path) -> None:
    _write_run(tmp_path, "run_a")

    data = load_run("run_a", tmp_path)

    assert data["config"]["name"] == "test_run"
    assert data["ground_truth"] == [1, 2, 3]
    assert data["beliefs"] == {"agent_0": []}
    # observations/metrics/divergence were never written for this run
    assert data["observations"] is None
    assert data["metrics"] is None
    assert data["divergence"] is None


def test_load_run_raises_for_unknown_run(tmp_path: Path) -> None:
    with pytest.raises(RunNotFoundError):
        load_run("nope", tmp_path)


@pytest.mark.parametrize("malicious_id", ["..", "../secrets", "a/../../b", "a\\b"])
def test_load_run_rejects_path_traversal_attempts(tmp_path: Path, malicious_id: str) -> None:
    with pytest.raises(RunNotFoundError):
        load_run(malicious_id, tmp_path)
