from agents.metacognitive import MetacognitiveAgent
from core.observer import Observation


def test_evaluate_belief_reflects_last_confidence_and_evidence() -> None:
    agent = MetacognitiveAgent(seed=1)
    observation = Observation(temperature=20.0, light=0.9, object_position=(0, 0))

    agent.act(observation)
    evaluation = agent.evaluate_belief()

    assert evaluation.belief_id == "hidden_state_is_a"
    assert evaluation.confidence == max(agent.world_model.belief_a, agent.world_model.belief_b)
    assert evaluation.evidence == ["observed_light=0.9000"]


def test_evaluate_unset_belief_id_has_zero_confidence() -> None:
    agent = MetacognitiveAgent(seed=1)
    evaluation = agent.evaluate_belief("never_updated")
    assert evaluation.confidence == 0.0


def test_high_confidence_exploits_toward_higher_probability_state() -> None:
    # A long run of strongly-A-consistent light readings should push
    # confidence above the default 0.7 threshold and settle on guess_A.
    agent = MetacognitiveAgent(seed=1)
    for _ in range(50):
        agent.act(Observation(temperature=20.0, light=0.95, object_position=(0, 0)))

    assert agent.world_model.belief_a > 0.7
    action = agent.act(Observation(temperature=20.0, light=0.95, object_position=(0, 0)))
    assert action.name == "guess_A"


def test_low_confidence_explores_instead_of_always_committing_to_slim_lead() -> None:
    # An observation exactly between the two hypothesis means keeps
    # belief pinned near the uninformative 0.5/0.5 prior, so confidence
    # never crosses the (deliberately unreachable) 0.99 threshold - every
    # act() should explore instead of committing to a fixed guess.
    agent = MetacognitiveAgent(seed=1, confidence_threshold=0.99)
    midpoint_observation = Observation(temperature=20.0, light=0.5, object_position=(0, 0))

    guesses = {agent.act(midpoint_observation).name for _ in range(30)}

    assert guesses == {"guess_A", "guess_B"}
