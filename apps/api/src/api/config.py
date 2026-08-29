import os
from dataclasses import dataclass
from enum import StrEnum


class IntentParserMode(StrEnum):
    MOCK = "mock"
    CLAUDE = "claude"


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
    intent_parser_mode: IntentParserMode = IntentParserMode.CLAUDE
    intent_parser_fallback_to_mock: bool = False
    anthropic_api_key: str | None = None
    claude_model: str = "claude-haiku-4-5-20251001"
    claude_timeout_seconds: float = 10.0
    database_url: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        mode_value = os.getenv("INTENT_PARSER_MODE", IntentParserMode.CLAUDE.value).lower()
        try:
            mode = IntentParserMode(mode_value)
        except ValueError as exc:
            raise ValueError("INTENT_PARSER_MODE must be 'mock' or 'claude'") from exc

        timeout_seconds = float(os.getenv("CLAUDE_TIMEOUT_SECONDS", "10"))
        if timeout_seconds <= 0:
            raise ValueError("CLAUDE_TIMEOUT_SECONDS must be greater than zero")

        fallback_value = os.getenv("INTENT_PARSER_FALLBACK_TO_MOCK", "false").lower()
        if fallback_value not in {"true", "false"}:
            raise ValueError("INTENT_PARSER_FALLBACK_TO_MOCK must be 'true' or 'false'")

        api_key = os.getenv("ANTHROPIC_API_KEY") or None
        database_url = os.getenv("DATABASE_URL") or None
        model = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001").strip()
        if not model:
            raise ValueError("CLAUDE_MODEL cannot be empty")

        if mode == IntentParserMode.CLAUDE and api_key is None:
            raise ValueError("ANTHROPIC_API_KEY is required when INTENT_PARSER_MODE=claude")

        return cls(
            intent_parser_mode=mode,
            intent_parser_fallback_to_mock=fallback_value == "true",
            anthropic_api_key=api_key,
            claude_model=model,
            claude_timeout_seconds=timeout_seconds,
            database_url=database_url,
        )
