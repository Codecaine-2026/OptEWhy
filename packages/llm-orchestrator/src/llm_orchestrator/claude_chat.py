import json
import logging
from typing import Protocol

import anthropic

from llm_orchestrator.chat import ChatResponder
from llm_orchestrator.parsers import IntentParserUnavailableError

logger = logging.getLogger(__name__)


class _TextBlock(Protocol):
    type: str
    text: str


class _MessageResponse(Protocol):
    content: list[_TextBlock]


class _MessagesAPI(Protocol):
    def create(self, **kwargs: object) -> _MessageResponse: ...


class _ClaudeClient(Protocol):
    messages: _MessagesAPI


class ClaudeChatResponder(ChatResponder):
    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        timeout_seconds: float = 10.0,
        client: _ClaudeClient | None = None,
    ) -> None:
        self._model = model
        self._client = client or anthropic.Anthropic(api_key=api_key, timeout=timeout_seconds)

    def respond(self, message: str) -> str:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=200,
                system=self._system_prompt(),
                messages=[{"role": "user", "content": message}],
            )
        except Exception as exc:
            logger.exception("Claude chat response failed")
            raise IntentParserUnavailableError("Claude chat response failed") from exc

        answer = "".join(block.text for block in response.content if block.type == "text").strip()
        if not answer:
            raise IntentParserUnavailableError("Claude returned an empty chat response")
        return answer

    def respond_to_analysis(
        self,
        *,
        message: str,
        causal_result: dict[str, object],
        evidence: list[dict[str, object]],
        scenario: dict[str, object] | None,
    ) -> str:
        payload = json.dumps(
            {
                "question": message,
                "causal_result": causal_result,
                "evidence": evidence,
                "scenario": scenario,
            },
            ensure_ascii=False,
        )
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=500,
                system=self._analysis_system_prompt(is_scenario=scenario is not None),
                messages=[{"role": "user", "content": payload}],
            )
        except Exception as exc:
            logger.exception("Claude analysis response failed")
            raise IntentParserUnavailableError("Claude analysis response failed") from exc

        answer = "".join(block.text for block in response.content if block.type == "text").strip()
        if not answer:
            raise IntentParserUnavailableError("Claude returned an empty analysis response")
        return answer

    @staticmethod
    def _system_prompt() -> str:
        return """You are the friendly AI Copilot for OptEWhy, a port-operations causal
intelligence app. Respond naturally and concisely to greetings and general conversation. Be helpful
and professional. Do not invent port metrics, causal findings, or analysis results in this
conversational mode."""

    @staticmethod
    def _analysis_system_prompt(*, is_scenario: bool) -> str:
        base_prompt = (
            "You explain causal-analysis results for a port operations copilot. Use only "
            "the supplied JSON data. Clearly distinguish modeled causal paths from "
            "evidence. Do not invent metrics, causes, or operational facts. Return Markdown. "
            "After a concise opening answer, make the second section ## Causal explanation. "
            "In that section, explain the modeled cause-and-effect flow in plain language, "
            "such as one factor increasing or decreasing the next factor and leading to the "
            "observed result. Do not reveal private reasoning or hidden chain-of-thought."
        )
        if not is_scenario:
            return base_prompt
        return (
            f"{base_prompt} This is a scenario simulation. Use concise sections named "
            "## Scenario summary, ## Causal explanation, ## Projected effects, and "
            "## Operational considerations. "
            "When scenario.structuredIntervention.targetNodeId is present, lead with the "
            "projected outcome for that requested target before describing other KPI effects. "
            "For a targeted scenario, causal_result.dominantPaths contains only modeled paths "
            "from the intervention to the requested target. If it is empty, clearly state that "
            "the model has no directed causal path and do not explain general target drivers as "
            "effects of the intervention. "
            "If the scenario input did not specify a change direction or magnitude, state the "
            "modeled 15% increase assumption explicitly. "
            "Present projected KPI effects in a valid GitHub-Flavored Markdown table, with a "
            "header row and one row per KPI. Keep every table row on its own line. Use bullets "
            "only for operational considerations, not for KPI comparisons or feedback loops."
        )
