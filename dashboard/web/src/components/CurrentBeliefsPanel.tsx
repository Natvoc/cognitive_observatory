import type { BeliefRecord } from "../types";

interface Props {
  beliefs: Record<string, BeliefRecord[]>;
}

export function CurrentBeliefsPanel({ beliefs }: Props) {
  const agentNames = Object.keys(beliefs).sort();

  return (
    <div className="panel">
      <h2>Beliefs actuales / predicción con confianza</h2>
      <table className="data-table">
        <thead>
          <tr>
            <th>agente</th>
            <th>predicted_hidden_state</th>
            <th>confidence</th>
          </tr>
        </thead>
        <tbody>
          {agentNames.map((agent) => {
            const records = beliefs[agent];
            const last = records[records.length - 1] as BeliefRecord | undefined;
            const confidenceText = last && last.confidence !== null ? last.confidence.toFixed(4) : "-";
            return (
              <tr key={agent}>
                <td>{agent}</td>
                <td>{last?.predicted_hidden_state ?? "-"}</td>
                <td>{confidenceText}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
