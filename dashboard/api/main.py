"""Read-only FastAPI over persisted experiment runs (spec §10, roadmap
Fase 6.1). Lists and returns already-run experiments from experiments/ -
it never executes anything. Run locally with:

    uvicorn dashboard.api.main:app --reload
"""

from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException

from agents.metacognitive import SelfModelDescription
from dashboard.api.agent_info import AgentTypeNotFoundError, get_agent_self_model
from dashboard.api.runs import (
    DEFAULT_EXPERIMENTS_DIR,
    RunNotFoundError,
    RunSummary,
    list_runs,
    load_run,
)

app = FastAPI(title="Cognitive Observatory API")


def get_experiments_dir() -> Path:
    return DEFAULT_EXPERIMENTS_DIR


@app.get("/runs")
def get_runs(experiments_dir: Path = Depends(get_experiments_dir)) -> list[RunSummary]:
    return list_runs(experiments_dir)


@app.get("/runs/{run_id}")
def get_run(
    run_id: str, experiments_dir: Path = Depends(get_experiments_dir)
) -> dict[str, Any]:
    try:
        return load_run(run_id, experiments_dir)
    except RunNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/agent-info/{agent_type}")
def get_agent_info(agent_type: str) -> SelfModelDescription:
    try:
        return get_agent_self_model(agent_type)
    except AgentTypeNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
