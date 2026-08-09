import { useEffect, useState } from "react";

import { fetchRun, fetchRuns } from "./api";
import { ObserverPanel } from "./components/ObserverPanel";
import { PredictionErrorChart } from "./components/PredictionErrorChart";
import { RunSelector } from "./components/RunSelector";
import { WorldPanel } from "./components/WorldPanel";
import type { RunData, RunSummary } from "./types";

export function App() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [runData, setRunData] = useState<RunData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRuns()
      .then(setRuns)
      .catch((err: unknown) => setError(String(err)));
  }, []);

  useEffect(() => {
    if (!selectedRunId) {
      setRunData(null);
      return;
    }
    setError(null);
    fetchRun(selectedRunId)
      .then(setRunData)
      .catch((err: unknown) => setError(String(err)));
  }, [selectedRunId]);

  return (
    <main>
      <h1>Cognitive Observatory</h1>
      <RunSelector runs={runs} selectedRunId={selectedRunId} onSelect={setSelectedRunId} />

      {error && <p className="error">{error}</p>}

      {runData && (
        <>
          <div className="side-by-side">
            {runData.ground_truth && <WorldPanel groundTruth={runData.ground_truth} />}
            {runData.beliefs && <ObserverPanel beliefs={runData.beliefs} />}
          </div>
          {runData.metrics && <PredictionErrorChart metrics={runData.metrics} />}
        </>
      )}
    </main>
  );
}
