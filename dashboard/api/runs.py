"""Read-only access to persisted experiment runs under experiments/
(roadmap Fase 6.1). Kept independent of FastAPI so listing/loading can be
tested directly, without spinning up an HTTP server. Never writes
anything and never executes an experiment - it only reads JSON that
Experiment.run() already wrote to disk.
"""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

DEFAULT_EXPERIMENTS_DIR = Path("experiments")

RUN_FILES = (
    "config",
    "ground_truth",
    "observations",
    "beliefs",
    "metrics",
    "divergence",
)


class RunNotFoundError(Exception):
    def __init__(self, run_id: str) -> None:
        super().__init__(f"run not found: {run_id!r}")
        self.run_id = run_id


class RunSummary(BaseModel):
    run_id: str
    name: str | None = None
    seed: int | None = None
    steps: int | None = None


def list_runs(experiments_dir: Path = DEFAULT_EXPERIMENTS_DIR) -> list[RunSummary]:
    if not experiments_dir.exists():
        return []

    summaries = []
    for entry in sorted(experiments_dir.iterdir()):
        config_path = entry / "config.json"
        if not entry.is_dir() or not config_path.exists():
            continue
        config = _read_json(config_path)
        summaries.append(
            RunSummary(
                run_id=entry.name,
                name=config.get("name"),
                seed=config.get("seed"),
                steps=config.get("steps"),
            )
        )
    return summaries


def load_run(run_id: str, experiments_dir: Path = DEFAULT_EXPERIMENTS_DIR) -> dict[str, Any]:
    _validate_run_id(run_id)
    run_dir = experiments_dir / run_id
    if not run_dir.is_dir():
        raise RunNotFoundError(run_id)

    data: dict[str, Any] = {}
    for key in RUN_FILES:
        path = run_dir / f"{key}.json"
        data[key] = _read_json(path) if path.exists() else None
    return data


def _validate_run_id(run_id: str) -> None:
    if not run_id or "/" in run_id or "\\" in run_id or ".." in run_id:
        raise RunNotFoundError(run_id)


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)
