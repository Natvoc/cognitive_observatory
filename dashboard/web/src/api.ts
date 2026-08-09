import type { RunData, RunSummary } from "./types";

const API_BASE = "/api";

async function getJSON<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`${path} -> HTTP ${response.status}`);
  }
  return (await response.json()) as T;
}

export function fetchRuns(): Promise<RunSummary[]> {
  return getJSON<RunSummary[]>("/runs");
}

export function fetchRun(runId: string): Promise<RunData> {
  return getJSON<RunData>(`/runs/${encodeURIComponent(runId)}`);
}
