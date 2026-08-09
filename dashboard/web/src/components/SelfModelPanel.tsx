import { useEffect, useState } from "react";

import { fetchAgentInfo } from "../api";
import type { SelfModelDescription } from "../types";

interface Props {
  agentNames: string[];
}

// Substring match on the agent's name, since run configs don't uniformly
// record an agent "type" field today (Fase 6.3 scope note - see the
// self-model discussion in the roadmap). The only architecture with a
// declared self-model right now is Agent 3 - Metacognitive.
const SELF_MODEL_AGENT_TYPES: Record<string, string> = {
  metacognitive: "metacognitive",
};

export function SelfModelPanel({ agentNames }: Props) {
  const [descriptions, setDescriptions] = useState<Record<string, SelfModelDescription>>({});

  const selfAwareAgents = agentNames.filter((name) =>
    Object.keys(SELF_MODEL_AGENT_TYPES).some((key) => name.includes(key)),
  );

  useEffect(() => {
    selfAwareAgents.forEach((agentName) => {
      const matchedType = Object.entries(SELF_MODEL_AGENT_TYPES).find(([key]) =>
        agentName.includes(key),
      )?.[1];
      if (!matchedType) return;
      fetchAgentInfo(matchedType)
        .then((description) => {
          setDescriptions((prev) => ({ ...prev, [agentName]: description }));
        })
        .catch(() => {
          // Best-effort panel: an agent without a reachable self-model
          // description just doesn't render a card for it.
        });
    });
    // Keyed on the joined names (not the array reference) since a new
    // array with the same names shouldn't re-trigger these fetches.
  }, [agentNames.join(",")]);

  if (selfAwareAgents.length === 0) {
    return (
      <div className="panel">
        <h2>Self-model</h2>
        <p className="note">Ningún agente de esta corrida declara capabilities/limitations.</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Self-model</h2>
      {selfAwareAgents.map((agentName) => {
        const description = descriptions[agentName];
        return (
          <div key={agentName} className="self-model-card">
            <h3>{agentName}</h3>
            {!description && <p className="note">Cargando...</p>}
            {description && (
              <>
                <p className="chart-label">capabilities</p>
                <ul>
                  {description.capabilities.map((capability) => (
                    <li key={capability}>{capability}</li>
                  ))}
                </ul>
                <p className="chart-label">limitations</p>
                <ul>
                  {description.limitations.map((limitation) => (
                    <li key={limitation}>{limitation}</li>
                  ))}
                </ul>
              </>
            )}
          </div>
        );
      })}
    </div>
  );
}
