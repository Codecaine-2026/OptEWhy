from llm_orchestrator.gemini_chat import GeminiChatResponder


class FakeResponse:
    text = "Hi! How can I help with your port operations?"


class FakeModelsAPI:
    def __init__(self) -> None:
        self.last_kwargs: dict[str, object] = {}

    def generate_content(self, **kwargs: object) -> FakeResponse:
        self.last_kwargs = kwargs
        return FakeResponse()


class FakeGeminiClient:
    def __init__(self, models: FakeModelsAPI) -> None:
        self.models = models


def test_gemini_chat_responder_generates_natural_language_reply() -> None:
    models = FakeModelsAPI()
    responder = GeminiChatResponder(
        model="gemini-3.6-flash",
        client=FakeGeminiClient(models),
    )

    answer = responder.respond("hi")

    assert answer == "Hi! How can I help with your port operations?"
    assert models.last_kwargs["model"] == "gemini-3.6-flash"
    assert models.last_kwargs["contents"] == "hi"
    assert "friendly AI Copilot" in str(models.last_kwargs["config"])
