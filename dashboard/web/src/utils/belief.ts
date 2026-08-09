import type { BeliefRecord } from "../types";

/** Reconstructs P(hidden_state=A) from a BeliefRecord - same convention
 * used in scripts/attention_experiment.py and core/reporting. */
export function beliefA(record: BeliefRecord): number {
  return record.predicted_hidden_state === "A" ? record.confidence : 1 - record.confidence;
}
