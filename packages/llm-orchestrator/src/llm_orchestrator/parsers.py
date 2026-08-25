from typing import Protocol

from llm_orchestrator.models import IntentType, StructuredQuery, Target


class IntentParser(Protocol):
    def parse(self, message: str) -> StructuredQuery: ...


class IntentParserError(RuntimeError):
    """Base error raised when a message cannot be converted into a structured query."""


class IntentParserUnavailableError(IntentParserError):
    """Raised when an external parser cannot return a usable result."""


class InvalidIntentTargetError(IntentParserError):
    """Raised when a parser selects a node outside the active causal graph."""


class MockIntentParser:
    def parse(self, message: str) -> StructuredQuery:
        lowered = message.lower()
        greetings = {
            "hi",
            "hello",
            "hey",
            "hey there",
            "good morning",
            "good afternoon",
            "good evening",
        }
        if lowered.strip() in greetings:
            return StructuredQuery(intent=IntentType.CASUAL_CONVERSATION, raw_message=message)
        if "what if" in lowered or "move" in lowered or "add" in lowered:
            return StructuredQuery(intent=IntentType.SCENARIO_SIMULATION, raw_message=message)
        if "report" in lowered or "evidence" in lowered:
            return StructuredQuery(intent=IntentType.EVIDENCE_LOOKUP, raw_message=message)
        if "how can" in lowered or "recommend" in lowered:
            return StructuredQuery(intent=IntentType.RECOMMENDATION, raw_message=message)
        if "would" in lowered and "if" in lowered:
            return StructuredQuery(intent=IntentType.COUNTERFACTUAL, raw_message=message)
        if "causing" in lowered or "feedback" in lowered or "loop" in lowered:
            return StructuredQuery(
                intent=IntentType.ROOT_MECHANISM_ANALYSIS,
                target=Target(
                    node_id="yard_density",
                    entity_type="yard_block",
                    entity_id="block_c",
                ),
                raw_message=message,
            )
        return StructuredQuery(
            intent=IntentType.ANOMALY_EXPLANATION,
            target=Target(node_id="qc_productivity", entity_type="vessel", entity_id="vessel_a"),
            raw_message=message,
        )


class FallbackIntentParser:
    """Use a deterministic parser only when the primary external service is unavailable."""

    def __init__(self, primary: IntentParser, fallback: IntentParser) -> None:
        self._primary = primary
        self._fallback = fallback

    def parse(self, message: str) -> StructuredQuery:
        try:
            return self._primary.parse(message)
        except IntentParserUnavailableError:
            return self._fallback.parse(message)
