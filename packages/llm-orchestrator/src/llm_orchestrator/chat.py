from typing import Protocol


class AnalysisResponder(Protocol):
    def respond_to_analysis(
        self,
        *,
        message: str,
        causal_result: dict[str, object],
        evidence: list[dict[str, object]],
        scenario: dict[str, object] | None,
    ) -> str: ...


class ChatResponder(Protocol):
    def respond(self, message: str) -> str: ...
