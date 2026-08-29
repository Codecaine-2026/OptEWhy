import os
from dataclasses import dataclass
from enum import StrEnum


class IntentParserMode(StrEnum):
    MOCK = "mock"
    GEMINI = "gemini"


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
    intent_parser_mode: IntentParserMode = IntentParserMode.GEMINI
    intent_parser_fallback_to_mock: bool = False
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.6-flash"
    gemini_timeout_seconds: float = 10.0

    @classmethod
    def from_env(cls) -> "Settings":
        mode_value = os.getenv("INTENT_PARSER_MODE", IntentParserMode.GEMINI.value).lower()
        try:
            mode = IntentParserMode(mode_value)
        except ValueError as exc:
            raise ValueError("INTENT_PARSER_MODE must be 'mock' or 'gemini'") from exc

        timeout_seconds = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "10"))
        if timeout_seconds <= 0:
            raise ValueError("GEMINI_TIMEOUT_SECONDS must be greater than zero")

        fallback_value = os.getenv("INTENT_PARSER_FALLBACK_TO_MOCK", "false").lower()
        if fallback_value not in {"true", "false"}:
            raise ValueError("INTENT_PARSER_FALLBACK_TO_MOCK must be 'true' or 'false'")

        api_key = os.getenv("GEMINI_API_KEY") or None
        model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()
        if not model:
            raise ValueError("GEMINI_MODEL cannot be empty")

        if mode == IntentParserMode.GEMINI and api_key is None:
            if fallback_value == "true":
                mode = IntentParserMode.MOCK
            else:
                raise ValueError("GEMINI_API_KEY is required when INTENT_PARSER_MODE=gemini")

        return cls(
            intent_parser_mode=mode,
            intent_parser_fallback_to_mock=fallback_value == "true",
            gemini_api_key=api_key,
            gemini_model=model,
            gemini_timeout_seconds=timeout_seconds,
        )
