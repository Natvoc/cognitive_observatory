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

export interface ObservationEntry {
  temperature: number;
  light: number;
  object_position: [number, number];
}

export interface BeliefRecord {
  predicted_hidden_state: string;
  // null for runs persisted before Fase 3 (agents without a world_model
  // reported no confidence) - see experiments/CHANGELOG.md.
  confidence: number | null;
}

export interface RunData {
  config: Record<string, unknown> | null;
  ground_truth: GroundTruthEntry[] | null;
  observations: ObservationEntry[] | null;
  beliefs: Record<string, BeliefRecord[]> | null;
  metrics: Record<string, number[]> | null;
  divergence: Record<string, number[]> | null;
}

export interface SelfModelDescription {
  capabilities: string[];
  limitations: string[];
}
