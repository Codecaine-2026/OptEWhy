import pytest
from api.config import IntentParserMode, Settings


def test_settings_default_to_gemini_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "INTENT_PARSER_MODE",
        "INTENT_PARSER_FALLBACK_TO_MOCK",
        "GEMINI_API_KEY",
        "GEMINI_MODEL",
        "GEMINI_TIMEOUT_SECONDS",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    settings = Settings.from_env()

    assert settings.intent_parser_mode == IntentParserMode.GEMINI
    assert settings.gemini_api_key == "test-key"
    assert settings.gemini_model == "gemini-3.6-flash"


def test_gemini_mode_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTENT_PARSER_MODE", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        Settings.from_env()


def test_gemini_mode_reads_server_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTENT_PARSER_MODE", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_MODEL", "test-model")
    monkeypatch.setenv("GEMINI_TIMEOUT_SECONDS", "4.5")
    monkeypatch.setenv("INTENT_PARSER_FALLBACK_TO_MOCK", "true")

    settings = Settings.from_env()

    assert settings.intent_parser_mode == IntentParserMode.GEMINI
    assert settings.gemini_model == "test-model"
    assert settings.gemini_timeout_seconds == 4.5
    assert settings.intent_parser_fallback_to_mock is True


def test_settings_reject_invalid_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_TIMEOUT_SECONDS", "0")

    with pytest.raises(ValueError, match="GEMINI_TIMEOUT_SECONDS"):
        Settings.from_env()
