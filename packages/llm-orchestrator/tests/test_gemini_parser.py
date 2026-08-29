import pytest
from llm_orchestrator.gemini_parser import GeminiIntentParser, IntentOutput
from llm_orchestrator.models import IntentType, StructuredQuery
from llm_orchestrator.parsers import (
    FallbackIntentParser,
    IntentParserUnavailableError,
    InvalidIntentTargetError,
    MockIntentParser,
)


class FakeResponse:
    def __init__(self, output: IntentOutput | None) -> None:
        self.text = output.model_dump_json() if output is not None else None


class FakeModelsAPI:
    def __init__(
        self,
        output: IntentOutput | None = None,
        error: Exception | None = None,
    ) -> None:
        self.output = output
        self.error = error
        self.last_kwargs: dict[str, object] = {}

    def generate_content(self, **kwargs: object) -> FakeResponse:
        self.last_kwargs = kwargs
        if self.error is not None:
            raise self.error
        return FakeResponse(self.output)


class FakeGeminiClient:
    def __init__(self, models: FakeModelsAPI) -> None:
        self.models = models


def build_output(
    *,
    intent: IntentType = IntentType.ANOMALY_EXPLANATION,
    node_id: str | None = "qc_productivity",
) -> IntentOutput:
    include_analysis = intent != IntentType.CASUAL_CONVERSATION
    target: dict[str, str | None] | None = None
    if node_id is not None and include_analysis:
        target = {
            "node_id": node_id,
            "entity_type": "vessel",
            "entity_id": "vessel_a",
        }
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


def build_parser(models: FakeModelsAPI) -> GeminiIntentParser:
    return GeminiIntentParser(
        node_catalog={
            "qc_productivity": "QC Productivity",
            "yard_density": "Yard Density",
        },
        model="test-model",
        client=FakeGeminiClient(models),
    )


def test_gemini_parser_builds_validated_structured_query() -> None:
    models = FakeModelsAPI(
        build_output(intent=IntentType.ROOT_MECHANISM_ANALYSIS, node_id="yard_density")
    )
    parser = build_parser(models)
    message = "Which mechanism is driving congestion in the yard?"

    query = parser.parse(message)

    assert query.intent == IntentType.ROOT_MECHANISM_ANALYSIS
    assert query.target is not None
    assert query.target.node_id == "yard_density"
    assert query.raw_message == message
    assert models.last_kwargs["model"] == "test-model"
    assert models.last_kwargs["contents"] == message
    config = models.last_kwargs["config"]
    assert "yard_density" in str(config)
    assert "What if yard density is 20% lower?" in str(config)
    assert "Intent decision rule" in str(config)
    assert config.response_schema is None
    assert config.response_json_schema == IntentOutput.model_json_schema()


@pytest.mark.parametrize(
    ("message", "intent"),
    [
        ("Hi", IntentType.CASUAL_CONVERSATION),
        ("Why did crane productivity fall?", IntentType.ANOMALY_EXPLANATION),
        ("Trace the congestion feedback loop.", IntentType.ROOT_MECHANISM_ANALYSIS),
        ("Suppose yard density rises next shift.", IntentType.SCENARIO_SIMULATION),
        ("Would the delay have cleared without rain?", IntentType.COUNTERFACTUAL),
        ("Which intervention should the operator take?", IntentType.RECOMMENDATION),
        ("Show the reports supporting that conclusion.", IntentType.EVIDENCE_LOOKUP),
    ],
)
def test_gemini_parser_accepts_every_supported_intent(
    message: str,
    intent: IntentType,
) -> None:
    parser = build_parser(FakeModelsAPI(build_output(intent=intent)))

    query = parser.parse(message)

    assert query.intent == intent


def test_gemini_parser_allows_ambiguous_target_to_remain_unset() -> None:
    parser = build_parser(
        FakeModelsAPI(build_output(intent=IntentType.EVIDENCE_LOOKUP, node_id=None))
    )

    query = parser.parse("Can I see the supporting report?")

    assert query.target is None


def test_gemini_parser_rejects_unknown_causal_node() -> None:
    parser = build_parser(FakeModelsAPI(build_output(node_id="invented_node")))

    with pytest.raises(InvalidIntentTargetError, match="invented_node"):
        parser.parse("Why is the invented metric low?")


@pytest.mark.parametrize(
    "models",
    [
        FakeModelsAPI(output=None),
        FakeModelsAPI(error=TimeoutError("timed out")),
    ],
)
def test_gemini_parser_reports_unavailable_service(models: FakeModelsAPI) -> None:
    parser = build_parser(models)

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
