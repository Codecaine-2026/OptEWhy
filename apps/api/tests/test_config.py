import pytest
from api.config import IntentParserMode, Settings


def test_settings_default_to_claude_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "INTENT_PARSER_MODE",
        "INTENT_PARSER_FALLBACK_TO_MOCK",
        "ANTHROPIC_API_KEY",
        "CLAUDE_MODEL",
        "CLAUDE_TIMEOUT_SECONDS",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    settings = Settings.from_env()

    assert settings.intent_parser_mode == IntentParserMode.CLAUDE
    assert settings.anthropic_api_key == "test-key"
    assert settings.claude_model == "claude-haiku-4-5-20251001"


def test_claude_mode_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTENT_PARSER_MODE", "claude")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        Settings.from_env()


def test_claude_mode_reads_server_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTENT_PARSER_MODE", "claude")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("CLAUDE_MODEL", "test-model")
    monkeypatch.setenv("CLAUDE_TIMEOUT_SECONDS", "4.5")
    monkeypatch.setenv("INTENT_PARSER_FALLBACK_TO_MOCK", "true")

    settings = Settings.from_env()

    assert settings.intent_parser_mode == IntentParserMode.CLAUDE
    assert settings.claude_model == "test-model"
    assert settings.claude_timeout_seconds == 4.5
    assert settings.intent_parser_fallback_to_mock is True


def test_settings_reject_invalid_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("CLAUDE_TIMEOUT_SECONDS", "0")

    with pytest.raises(ValueError, match="CLAUDE_TIMEOUT_SECONDS"):
        Settings.from_env()
