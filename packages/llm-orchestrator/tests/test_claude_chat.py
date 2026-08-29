from llm_orchestrator.claude_chat import ClaudeChatResponder


class FakeTextBlock:
    type = "text"
    text = "Hi! How can I help with your port operations?"


class FakeResponse:
    content = [FakeTextBlock()]


class FakeMessagesAPI:
    def __init__(self) -> None:
        self.last_kwargs: dict[str, object] = {}

    def create(self, **kwargs: object) -> FakeResponse:
        self.last_kwargs = kwargs
        return FakeResponse()


class FakeClaudeClient:
    def __init__(self, messages: FakeMessagesAPI) -> None:
        self.messages = messages


def test_claude_chat_responder_generates_natural_language_reply() -> None:
    messages = FakeMessagesAPI()
    responder = ClaudeChatResponder(model="test-model", client=FakeClaudeClient(messages))

    answer = responder.respond("hi")

    assert answer == "Hi! How can I help with your port operations?"
    assert messages.last_kwargs["model"] == "test-model"
    assert messages.last_kwargs["messages"] == [{"role": "user", "content": "hi"}]
    assert "friendly AI Copilot" in str(messages.last_kwargs["system"])


def test_claude_chat_responder_generates_grounded_analysis() -> None:
    messages = FakeMessagesAPI()
    responder = ClaudeChatResponder(model="test-model", client=FakeClaudeClient(messages))

    answer = responder.respond_to_analysis(
        message="Why is productivity low?",
        causal_result={"targetNodeId": "qc_productivity"},
        evidence=[],
        scenario=None,
    )

    assert answer == "Hi! How can I help with your port operations?"
    assert "causal-analysis results" in str(messages.last_kwargs["system"])
