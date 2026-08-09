/** Turns {agentName: values[]} into Recharts-friendly rows:
 * [{step: 0, agentA: v, agentB: v}, ...] - one line per agent, subsampled
 * for performance on long runs. */
export function mergeSeries(
  seriesByAgent: Record<string, number[]>,
  maxPoints = 500,
): Record<string, number>[] {
  const agentNames = Object.keys(seriesByAgent).sort();
  if (agentNames.length === 0) {
    return [];
  }

  const steps = seriesByAgent[agentNames[0]].length;
  const rows = Array.from({ length: steps }, (_, step) => {
    const row: Record<string, number> = { step };
    for (const agent of agentNames) {
      row[agent] = seriesByAgent[agent][step];
    }
    return row;
  });

  if (rows.length <= maxPoints) {
    return rows;
  }
  const sampleStep = rows.length / maxPoints;
  return Array.from({ length: maxPoints }, (_, i) => rows[Math.floor(i * sampleStep)]);
}

export const AGENT_COLORS = [
  "#2563eb",
  "#dc2626",
  "#16a34a",
  "#9333ea",
  "#ea580c",
  "#0891b2",
];

export function colorFor(agentIndex: number): string {
  return AGENT_COLORS[agentIndex % AGENT_COLORS.length];
}
