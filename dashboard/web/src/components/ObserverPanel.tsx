import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { BeliefRecord } from "../types";
import { beliefA } from "../utils/belief";
import { colorFor, mergeSeries } from "../utils/mergeSeries";

interface Props {
  beliefs: Record<string, BeliefRecord[]>;
}

export function ObserverPanel({ beliefs }: Props) {
  const agentNames = Object.keys(beliefs).sort();
  const beliefASeries = Object.fromEntries(
    agentNames.map((agent) => [agent, beliefs[agent].map(beliefA)]),
  );
  const rows = mergeSeries(beliefASeries);

  return (
    <div className="panel">
      <h2>Observer (belief P(hidden_state=A))</h2>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="step" tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Legend />
          {agentNames.map((agent, i) => (
            <Line
              key={agent}
              type="monotone"
              dataKey={agent}
              stroke={colorFor(i)}
              dot={false}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
