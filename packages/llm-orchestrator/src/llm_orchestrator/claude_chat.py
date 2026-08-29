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
                system=(
                    "You explain causal-analysis results for a port operations copilot. Use only "
                    "the supplied JSON data. Clearly distinguish modeled causal paths from "
                    "evidence. Do not invent metrics, causes, or operational facts."
                ),
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
