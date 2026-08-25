import logging
from typing import Protocol, cast

from google import genai
from google.genai import types

from llm_orchestrator.chat import ChatResponder
from llm_orchestrator.parsers import IntentParserUnavailableError

logger = logging.getLogger(__name__)


class _GeneratedResponse(Protocol):
    text: str | None


class _ModelsAPI(Protocol):
    def generate_content(self, **kwargs: object) -> _GeneratedResponse: ...


class _GeminiClient(Protocol):
    models: _ModelsAPI


class GeminiChatResponder(ChatResponder):
    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        timeout_seconds: float = 10.0,
        client: _GeminiClient | None = None,
    ) -> None:
        self._model = model
        self._client = client or cast(
            _GeminiClient,
            genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=int(timeout_seconds * 1000)),
            ),
        )

    def respond(self, message: str) -> str:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=message,
                config=types.GenerateContentConfig(system_instruction=self._system_prompt()),
            )
        except Exception as exc:
            logger.exception("Gemini chat response failed")
            raise IntentParserUnavailableError("Gemini chat response failed") from exc

        if not response.text:
            raise IntentParserUnavailableError("Gemini returned an empty chat response")
        return response.text.strip()

    @staticmethod
    def _system_prompt() -> str:
        return """You are the friendly AI Copilot for OptEWhy, a port-operations causal
intelligence app.
Respond naturally and concisely to greetings and general conversation. Be helpful and professional.
Do not invent port metrics, causal findings, or analysis results in this conversational mode.
"""
