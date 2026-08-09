import type { RunSummary } from "../types";

interface Props {
  runs: RunSummary[];
  selectedRunId: string | null;
  onSelect: (runId: string) => void;
}

export function RunSelector({ runs, selectedRunId, onSelect }: Props) {
  return (
    <select
      value={selectedRunId ?? ""}
      onChange={(event) => onSelect(event.target.value)}
      aria-label="Elegir corrida"
    >
      <option value="" disabled>
        Elegir corrida...
      </option>
      {runs.map((run) => (
        <option key={run.run_id} value={run.run_id}>
          {run.name ?? run.run_id} (seed={run.seed ?? "?"}, steps={run.steps ?? "?"})
        </option>
      ))}
    </select>
  );
}
