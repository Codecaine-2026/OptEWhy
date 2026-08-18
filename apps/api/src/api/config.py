import os
from dataclasses import dataclass
from enum import StrEnum


class IntentParserMode(StrEnum):
    MOCK = "mock"
    OPENAI = "openai"


DEFAULT_CORS_ALLOWED_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


def get_cors_allowed_origins() -> list[str]:
    configured = os.getenv("CORS_ALLOWED_ORIGINS")
    if configured is None:
        return list(DEFAULT_CORS_ALLOWED_ORIGINS)

    origins = [origin.strip() for origin in configured.split(",") if origin.strip()]
    if not origins:
        raise ValueError("CORS_ALLOWED_ORIGINS must contain at least one origin")
    return origins


@dataclass(frozen=True)
class Settings:
    intent_parser_mode: IntentParserMode = IntentParserMode.MOCK
    intent_parser_fallback_to_mock: bool = False
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    openai_timeout_seconds: float = 10.0

    @classmethod
    def from_env(cls) -> "Settings":
        mode_value = os.getenv("INTENT_PARSER_MODE", IntentParserMode.MOCK.value).lower()
        try:
            mode = IntentParserMode(mode_value)
        except ValueError as exc:
            raise ValueError("INTENT_PARSER_MODE must be 'mock' or 'openai'") from exc

        timeout_seconds = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "10"))
        if timeout_seconds <= 0:
            raise ValueError("OPENAI_TIMEOUT_SECONDS must be greater than zero")

        fallback_value = os.getenv("INTENT_PARSER_FALLBACK_TO_MOCK", "false").lower()
        if fallback_value not in {"true", "false"}:
            raise ValueError("INTENT_PARSER_FALLBACK_TO_MOCK must be 'true' or 'false'")

        api_key = os.getenv("OPENAI_API_KEY") or None
        model = os.getenv("OPENAI_MODEL", "gpt-5-mini").strip()
        if not model:
            raise ValueError("OPENAI_MODEL cannot be empty")
        if mode == IntentParserMode.OPENAI and api_key is None:
            raise ValueError("OPENAI_API_KEY is required when INTENT_PARSER_MODE=openai")

        return cls(
            intent_parser_mode=mode,
            intent_parser_fallback_to_mock=fallback_value == "true",
            openai_api_key=api_key,
            openai_model=model,
            openai_timeout_seconds=timeout_seconds,
        )
