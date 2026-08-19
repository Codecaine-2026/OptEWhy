from functools import lru_cache

from llm_orchestrator.openai_parser import OpenAIIntentParser
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
    parser: IntentParser = OpenAIIntentParser(
        node_catalog=node_catalog,
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        reasoning_effort=settings.openai_reasoning_effort,
        timeout_seconds=settings.openai_timeout_seconds,
    )
    if settings.intent_parser_fallback_to_mock:
        parser = FallbackIntentParser(parser, MockIntentParser())
    return parser


def get_query_orchestrator() -> QueryOrchestrator:
    return QueryOrchestrator(parser=get_intent_parser())


def get_scenario_orchestrator() -> ScenarioOrchestrator:
    return ScenarioOrchestrator()
