import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { GroundTruthEntry } from "../types";
import { subsample } from "../utils/subsample";

interface Props {
  groundTruth: GroundTruthEntry[];
}

export function WorldPanel({ groundTruth }: Props) {
  const rows = subsample(
    groundTruth.map((entry) => ({
      step: entry.timestamp,
      light: (entry.variables.light as number | undefined) ?? null,
      // hidden_state is never observable by the agent (spec §2) - this
      // panel shows the real World state, so it's fair game here.
      hidden_state: entry.causal_state.hidden_state === "A" ? 1 : 0,
    })),
  );

  return (
    <div className="panel">
      <h2>World (ground truth)</h2>
      <p className="chart-label">light</p>
      <ResponsiveContainer width="100%" height={120}>
        <LineChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="step" tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Line type="monotone" dataKey="light" stroke="#0891b2" dot={false} />
        </LineChart>
      </ResponsiveContainer>

      <p className="chart-label">hidden_state (1=A, 0=B)</p>
      <ResponsiveContainer width="100%" height={80}>
        <LineChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="step" tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 1]} ticks={[0, 1]} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Line type="stepAfter" dataKey="hidden_state" stroke="#666" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
