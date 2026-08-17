from llm_orchestrator.models import IntentType, StructuredQuery, Target


class MockIntentParser:
    def parse(self, message: str) -> StructuredQuery:
        lowered = message.lower()
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
