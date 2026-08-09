export interface RunSummary {
  run_id: string;
  name: string | null;
  seed: number | null;
  steps: number | null;
}

export interface GroundTruthEntry {
  timestamp: number;
  variables: Record<string, unknown>;
  entities: Record<string, unknown>;
  causal_state: Record<string, unknown>;
}

export interface BeliefRecord {
  predicted_hidden_state: string;
  confidence: number;
}

export interface RunData {
  config: Record<string, unknown> | null;
  ground_truth: GroundTruthEntry[] | null;
  observations: unknown[] | null;
  beliefs: Record<string, BeliefRecord[]> | null;
  metrics: Record<string, number[]> | null;
  divergence: Record<string, number[]> | null;
}
