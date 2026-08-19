import pytest
from api.config import IntentParserMode, Settings


def test_settings_default_to_openai_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "INTENT_PARSER_MODE",
        "INTENT_PARSER_FALLBACK_TO_MOCK",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "OPENAI_REASONING_EFFORT",
        "OPENAI_TIMEOUT_SECONDS",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    settings = Settings.from_env()

    assert settings.intent_parser_mode == IntentParserMode.OPENAI
    assert settings.openai_api_key == "test-key"
    assert settings.openai_model == "gpt-5.6-luna"
    assert settings.openai_reasoning_effort == "low"


def test_openai_mode_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTENT_PARSER_MODE", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        Settings.from_env()


def test_openai_mode_reads_server_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTENT_PARSER_MODE", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "high")
    monkeypatch.setenv("OPENAI_TIMEOUT_SECONDS", "4.5")
    monkeypatch.setenv("INTENT_PARSER_FALLBACK_TO_MOCK", "true")

    settings = Settings.from_env()

    assert settings.intent_parser_mode == IntentParserMode.OPENAI
    assert settings.openai_model == "test-model"
    assert settings.openai_reasoning_effort == "high"
    assert settings.openai_timeout_seconds == 4.5
    assert settings.intent_parser_fallback_to_mock is True


def test_settings_reject_invalid_reasoning_effort(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "maximum")

    with pytest.raises(ValueError, match="OPENAI_REASONING_EFFORT"):
        Settings.from_env()
