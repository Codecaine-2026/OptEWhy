from llm_orchestrator.explanation import BackendGroundedExplanationBuilder


class ExplanationBuilder:
    def __init__(self) -> None:
        self._builder = BackendGroundedExplanationBuilder()

    def build(self, causal_result: dict[str, object], evidence: list[dict[str, object]]) -> str:
        return str(self._builder.build(causal_result, evidence))
