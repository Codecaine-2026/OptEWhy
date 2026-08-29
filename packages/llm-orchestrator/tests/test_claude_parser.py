import pytest
from llm_orchestrator.claude_parser import ClaudeIntentParser, IntentOutput
from llm_orchestrator.models import IntentType, StructuredQuery
from llm_orchestrator.parsers import (
    FallbackIntentParser,
    IntentParserUnavailableError,
    InvalidIntentTargetError,
    MockIntentParser,
)


class FakeTextBlock:
    type = "text"

    def __init__(self, text: str) -> None:
        self.text = text


class FakeResponse:
    def __init__(self, output: IntentOutput | None) -> None:
        self.content = [] if output is None else [FakeTextBlock(output.model_dump_json()[1:])]


class FakeMessagesAPI:
    def __init__(self, output: IntentOutput | None = None, error: Exception | None = None) -> None:
        self.output = output
        self.error = error
        self.last_kwargs: dict[str, object] = {}

    def create(self, **kwargs: object) -> FakeResponse:
        self.last_kwargs = kwargs
        if self.error is not None:
            raise self.error
        return FakeResponse(self.output)


class FakeClaudeClient:
    def __init__(self, messages: FakeMessagesAPI) -> None:
        self.messages = messages


def build_output(
    *, intent: IntentType = IntentType.ANOMALY_EXPLANATION, node_id: str | None = "qc_productivity"
) -> IntentOutput:
    include_analysis = intent != IntentType.CASUAL_CONVERSATION
    target = (
        {"node_id": node_id, "entity_type": "vessel", "entity_id": "vessel_a"}
        if node_id is not None and include_analysis
        else None
    )
    return IntentOutput.model_validate(
        {
            "intent": intent,
            "target": target,
            "time_window": {"mode": "current_shift", "start": None, "end": None},
            "analysis_options": {
                "include_paths": include_analysis,
                "include_loops": include_analysis,
                "include_evidence": include_analysis,
                "include_recommendations": intent == IntentType.RECOMMENDATION,
            },
        }
    )


def build_parser(messages: FakeMessagesAPI) -> ClaudeIntentParser:
    return ClaudeIntentParser(
        node_catalog={"qc_productivity": "QC Productivity", "yard_density": "Yard Density"},
        model="test-model",
        client=FakeClaudeClient(messages),
    )


def test_claude_parser_builds_validated_structured_query() -> None:
    messages = FakeMessagesAPI(
        build_output(intent=IntentType.ROOT_MECHANISM_ANALYSIS, node_id="yard_density")
    )
    parser = build_parser(messages)

    query = parser.parse("Which mechanism is driving congestion in the yard?")

    assert query.intent == IntentType.ROOT_MECHANISM_ANALYSIS
    assert query.target is not None
    assert query.target.node_id == "yard_density"
    assert messages.last_kwargs["model"] == "test-model"
    assert messages.last_kwargs["messages"] == [
        {"role": "user", "content": "Which mechanism is driving congestion in the yard?"},
        {"role": "assistant", "content": "{"},
    ]
    assert "yard_density" in str(messages.last_kwargs["system"])


def test_claude_parser_separates_scenario_intervention_from_requested_target() -> None:
    output = IntentOutput.model_validate(
        {
            **build_output(intent=IntentType.SCENARIO_SIMULATION, node_id="qc_productivity").model_dump(),
            "intervention": {
                "node_id": "yard_density",
                "operation": "increase_relative",
                "value": 0.1,
            },
        }
    )
    parser = build_parser(FakeMessagesAPI(output))

    query = parser.parse("What happens to QC productivity if yard density increases by 10%?")

    assert query.target is not None
    assert query.target.node_id == "qc_productivity"
    assert query.intervention is not None
    assert query.intervention.node_id == "yard_density"
    assert query.intervention.operation == "increase_relative"
    assert query.intervention.value == 0.1


def test_claude_parser_rejects_unknown_causal_node() -> None:
    parser = build_parser(FakeMessagesAPI(build_output(node_id="invented_node")))

    with pytest.raises(InvalidIntentTargetError, match="invented_node"):
        parser.parse("Why is the invented metric low?")


@pytest.mark.parametrize("output", [None, build_output(intent=IntentType.CASUAL_CONVERSATION)])
def test_claude_parser_reports_invalid_or_empty_responses(output: IntentOutput | None) -> None:
    parser = build_parser(FakeMessagesAPI(output))
    if output is not None:
        parser._client.messages.create = lambda **_: FakeResponse(None)  # type: ignore[method-assign]

    with pytest.raises(IntentParserUnavailableError):
        parser.parse("Why is productivity low?")


def test_fallback_parser_uses_mock_only_for_unavailable_primary() -> None:
    class UnavailableParser:
        def parse(self, message: str) -> StructuredQuery:
            raise IntentParserUnavailableError("offline")

    query = FallbackIntentParser(UnavailableParser(), MockIntentParser()).parse(
        "What if we move containers out of Block B?"
    )

    assert query.intent == IntentType.SCENARIO_SIMULATION
