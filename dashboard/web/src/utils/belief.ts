import type { BeliefRecord } from "../types";

/** Reconstructs P(hidden_state=A) from a BeliefRecord - same convention
 * used in scripts/attention_experiment.py and core/reporting.
 *
 * confidence is null for runs persisted before Fase 3 (agents without a
 * world_model reported no confidence at all - see experiments/CHANGELOG.md).
 * Must return null rather than silently computing a value: `1 - null`
 * evaluates to `1` in JS, which would make a null-confidence "guess_B"
 * record read as "100% certain it's A" - exactly backwards. */
export function beliefA(record: BeliefRecord): number | null {
  if (record.confidence === null) {
    return null;
  }
  return record.predicted_hidden_state === "A" ? record.confidence : 1 - record.confidence;
}
