from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from dashboard.api.main import app, get_experiments_dir


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    run_dir = tmp_path / "2026-01-01_hidden_variable_42"
    run_dir.mkdir()
    (run_dir / "config.json").write_text(
        '{"name": "hidden_variable", "seed": 42, "steps": 3}', encoding="utf-8"
    )
    (run_dir / "ground_truth.json").write_text("[1, 2, 3]", encoding="utf-8")
    (run_dir / "beliefs.json").write_text('{"agent_0": []}', encoding="utf-8")

    app.dependency_overrides[get_experiments_dir] = lambda: tmp_path
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_runs_lists_available_runs(client: TestClient) -> None:
    response = client.get("/runs")

    assert response.status_code == 200
    runs = response.json()
    assert len(runs) == 1
    assert runs[0]["run_id"] == "2026-01-01_hidden_variable_42"
    assert runs[0]["name"] == "hidden_variable"
    assert runs[0]["seed"] == 42


def test_get_run_returns_full_run_contents(client: TestClient) -> None:
    response = client.get("/runs/2026-01-01_hidden_variable_42")

    assert response.status_code == 200
    data = response.json()
    assert data["config"]["name"] == "hidden_variable"
    assert data["ground_truth"] == [1, 2, 3]
    assert data["beliefs"] == {"agent_0": []}
    assert data["metrics"] is None


def test_get_run_returns_404_for_unknown_run(client: TestClient) -> None:
    response = client.get("/runs/does_not_exist")
    assert response.status_code == 404


def test_get_run_returns_404_for_path_traversal_attempt(client: TestClient) -> None:
    response = client.get("/runs/..%2Fsecrets")
    assert response.status_code == 404


def test_get_agent_info_returns_metacognitive_description(client: TestClient) -> None:
    response = client.get("/agent-info/metacognitive")

    assert response.status_code == 200
    data = response.json()
    assert data["capabilities"]
    assert data["limitations"]


def test_get_agent_info_returns_404_for_unknown_agent_type(client: TestClient) -> None:
    response = client.get("/agent-info/does_not_exist")
    assert response.status_code == 404
