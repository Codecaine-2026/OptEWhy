from llm_orchestrator.models import IntentType
from llm_orchestrator.parsers import MockIntentParser


def test_parser_detects_scenario() -> None:
    query = MockIntentParser().parse("What if we move 15% of Block B containers?")

    assert query.intent == IntentType.SCENARIO_SIMULATION


def test_parser_defaults_to_anomaly_explanation() -> None:
    query = MockIntentParser().parse("Why is Vessel A productivity low?")

    assert query.intent == IntentType.ANOMALY_EXPLANATION
    assert query.target is not None

