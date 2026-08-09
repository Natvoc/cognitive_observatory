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

import { colorFor, mergeSeries } from "../utils/mergeSeries";

interface Props {
  metrics: Record<string, number[]>;
}

export function PredictionErrorChart({ metrics }: Props) {
  const agentNames = Object.keys(metrics).sort();
  const rows = mergeSeries(metrics);

  return (
    <div className="panel">
      <h2>prediction_error en el tiempo</h2>
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
