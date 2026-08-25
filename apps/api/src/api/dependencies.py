from functools import lru_cache

from llm_orchestrator.chat import ChatResponder
from llm_orchestrator.gemini_chat import GeminiChatResponder
from llm_orchestrator.gemini_parser import GeminiIntentParser
from llm_orchestrator.parsers import FallbackIntentParser, IntentParser, MockIntentParser

from api.config import IntentParserMode, Settings
from api.services.demo_data import build_demo_graph
from api.services.query_orchestrator import QueryOrchestrator
from api.services.scenario_orchestrator import ScenarioOrchestrator


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()


@lru_cache
def get_intent_parser() -> IntentParser:
    settings = get_settings()
    if settings.intent_parser_mode == IntentParserMode.MOCK:
        return MockIntentParser()

    graph = build_demo_graph()
    node_catalog = {node.id: node.label for node in graph.nodes}
    parser: IntentParser = GeminiIntentParser(
        node_catalog=node_catalog,
        model=settings.gemini_model,
        api_key=settings.gemini_api_key,
        timeout_seconds=settings.gemini_timeout_seconds,
    )
    if settings.intent_parser_fallback_to_mock:
        parser = FallbackIntentParser(parser, MockIntentParser())
    return parser


def get_query_orchestrator() -> QueryOrchestrator:
    settings = get_settings()
    chat_responder: ChatResponder | None = None
    if settings.intent_parser_mode == IntentParserMode.GEMINI:
        chat_responder = GeminiChatResponder(
            model=settings.gemini_model,
            api_key=settings.gemini_api_key,
            timeout_seconds=settings.gemini_timeout_seconds,
        )
    return QueryOrchestrator(parser=get_intent_parser(), chat_responder=chat_responder)


def get_scenario_orchestrator() -> ScenarioOrchestrator:
    return ScenarioOrchestrator()
