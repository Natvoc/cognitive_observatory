import type { BeliefRecord, GroundTruthEntry, ObservationEntry } from "../types";

interface Props {
  groundTruth: GroundTruthEntry[];
  observations: ObservationEntry[];
  beliefs: Record<string, BeliefRecord[]>;
  windowSize?: number;
}

export function RecentHistoryPanel({
  groundTruth,
  observations,
  beliefs,
  windowSize = 20,
}: Props) {
  const agentNames = Object.keys(beliefs).sort();
  const totalSteps = groundTruth.length;
  const start = Math.max(0, totalSteps - windowSize);
  const indices = Array.from({ length: totalSteps - start }, (_, i) => start + i);

  return (
    <div className="panel">
      <h2>Historial reciente (últimos {indices.length} steps)</h2>
      <p className="note">
        Reconstruido a partir de los datos ya persistidos de la corrida
        (observations.json + beliefs.json + ground_truth.json) — <strong>no</strong> es
        el subsistema de Episodic Memory formal (01_spec_proyecto.md §4.4), que todavía
        no está implementado.
      </p>
      <div className="table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              <th>step</th>
              <th>light</th>
              <th>hidden_state real</th>
              {agentNames.map((agent) => (
                <th key={agent}>{agent}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {indices.map((i) => {
              const trueState = groundTruth[i]?.causal_state.hidden_state as string | undefined;
              return (
                <tr key={i}>
                  <td>{i}</td>
                  <td>{observations[i]?.light.toFixed(4) ?? "-"}</td>
                  <td>{trueState ?? "-"}</td>
                  {agentNames.map((agent) => {
                    const record = beliefs[agent][i];
                    const correct = record && trueState && record.predicted_hidden_state === trueState;
                    return (
                      <td key={agent} className={correct ? "correct" : "incorrect"}>
                        {record?.predicted_hidden_state ?? "-"}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
