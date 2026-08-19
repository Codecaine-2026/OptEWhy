import pytest
from llm_orchestrator.models import IntentType, StructuredQuery
from llm_orchestrator.openai_parser import OpenAIIntentOutput, OpenAIIntentParser
from llm_orchestrator.parsers import (
    FallbackIntentParser,
    IntentParserUnavailableError,
    InvalidIntentTargetError,
    MockIntentParser,
)


class FakeResponse:
    def __init__(self, output: OpenAIIntentOutput | None) -> None:
        self.output_parsed = output


class FakeResponsesAPI:
    def __init__(
        self,
        output: OpenAIIntentOutput | None = None,
        error: Exception | None = None,
    ) -> None:
        self.output = output
        self.error = error
        self.last_kwargs: dict[str, object] = {}

    def parse(self, **kwargs: object) -> FakeResponse:
        self.last_kwargs = kwargs
        if self.error is not None:
            raise self.error
        return FakeResponse(self.output)


class FakeOpenAIClient:
    def __init__(self, responses: FakeResponsesAPI) -> None:
        self.responses = responses


def build_output(
    *,
    intent: IntentType = IntentType.ANOMALY_EXPLANATION,
    node_id: str | None = "qc_productivity",
) -> OpenAIIntentOutput:
    target: dict[str, str | None] | None = None
    if node_id is not None:
        target = {
            "node_id": node_id,
            "entity_type": "vessel",
            "entity_id": "vessel_a",
        }
    return OpenAIIntentOutput.model_validate(
        {
            "intent": intent,
            "target": target,
            "time_window": {"mode": "current_shift", "start": None, "end": None},
            "analysis_options": {
                "include_paths": True,
                "include_loops": True,
                "include_evidence": True,
                "include_recommendations": intent == IntentType.RECOMMENDATION,
            },
        }
    )


def build_parser(responses: FakeResponsesAPI) -> OpenAIIntentParser:
    return OpenAIIntentParser(
        node_catalog={
            "qc_productivity": "QC Productivity",
            "yard_density": "Yard Density",
        },
        model="test-model",
        client=FakeOpenAIClient(responses),
    )


def test_openai_parser_builds_validated_structured_query() -> None:
    responses = FakeResponsesAPI(
        build_output(intent=IntentType.ROOT_MECHANISM_ANALYSIS, node_id="yard_density")
    )
    parser = build_parser(responses)
    message = "Which mechanism is driving congestion in the yard?"

    query = parser.parse(message)

    assert query.intent == IntentType.ROOT_MECHANISM_ANALYSIS
    assert query.target is not None
    assert query.target.node_id == "yard_density"
    assert query.raw_message == message
    assert responses.last_kwargs["model"] == "test-model"
    assert responses.last_kwargs["reasoning"] == {"effort": "low"}
    assert responses.last_kwargs["text_format"] is OpenAIIntentOutput
    prompt_input = responses.last_kwargs["input"]
    assert isinstance(prompt_input, list)
    assert "yard_density" in str(prompt_input[0])


@pytest.mark.parametrize(
    ("message", "intent"),
    [
        ("Why did crane productivity fall?", IntentType.ANOMALY_EXPLANATION),
        ("Trace the congestion feedback loop.", IntentType.ROOT_MECHANISM_ANALYSIS),
        ("Suppose yard density rises next shift.", IntentType.SCENARIO_SIMULATION),
        ("Would the delay have cleared without rain?", IntentType.COUNTERFACTUAL),
        ("Which intervention should the operator take?", IntentType.RECOMMENDATION),
        ("Show the reports supporting that conclusion.", IntentType.EVIDENCE_LOOKUP),
    ],
)
def test_openai_parser_accepts_every_supported_intent(
    message: str,
    intent: IntentType,
) -> None:
    parser = build_parser(FakeResponsesAPI(build_output(intent=intent)))

    query = parser.parse(message)

    assert query.intent == intent


def test_openai_parser_allows_ambiguous_target_to_remain_unset() -> None:
    parser = build_parser(
        FakeResponsesAPI(build_output(intent=IntentType.EVIDENCE_LOOKUP, node_id=None))
    )

    query = parser.parse("Can I see the supporting report?")

    assert query.target is None


def test_openai_parser_rejects_unknown_causal_node() -> None:
    parser = build_parser(FakeResponsesAPI(build_output(node_id="invented_node")))

    with pytest.raises(InvalidIntentTargetError, match="invented_node"):
        parser.parse("Why is the invented metric low?")


@pytest.mark.parametrize(
    "responses",
    [
        FakeResponsesAPI(output=None),
        FakeResponsesAPI(error=TimeoutError("timed out")),
    ],
)
def test_openai_parser_reports_unavailable_service(responses: FakeResponsesAPI) -> None:
    parser = build_parser(responses)

    with pytest.raises(IntentParserUnavailableError):
        parser.parse("Why is productivity low?")


class UnavailableParser:
    def parse(self, message: str) -> StructuredQuery:
        raise IntentParserUnavailableError("offline")


def test_fallback_parser_uses_mock_only_for_unavailable_primary() -> None:
    parser = FallbackIntentParser(
        primary=UnavailableParser(),
        fallback=MockIntentParser(),
    )

    query = parser.parse("What if we move containers out of Block B?")

    assert query.intent == IntentType.SCENARIO_SIMULATION
