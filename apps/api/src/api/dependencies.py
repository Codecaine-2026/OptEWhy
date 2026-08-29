import os
from functools import lru_cache

from llm_orchestrator.chat import AnalysisResponder, ChatResponder
from llm_orchestrator.claude_chat import ClaudeChatResponder
from llm_orchestrator.claude_parser import ClaudeIntentParser
from llm_orchestrator.parsers import FallbackIntentParser, IntentParser, MockIntentParser

from api.config import IntentParserMode, Settings
from api.services.graph_repository import (
    GraphRepository,
    PostgresGraphRepository,
)
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

    graph = get_graph_repository().get_graph("terminal_alpha")
    node_catalog = {node.id: node.label for node in graph.nodes}
    parser: IntentParser = ClaudeIntentParser(
        node_catalog=node_catalog,
        model=settings.claude_model,
        api_key=settings.anthropic_api_key,
        timeout_seconds=settings.claude_timeout_seconds,
    )
    if settings.intent_parser_fallback_to_mock:
        parser = FallbackIntentParser(parser, MockIntentParser())
    return parser


@lru_cache
def get_graph_repository() -> GraphRepository:
    database_url = os.getenv("DATABASE_URL") or None
    mode = os.getenv("GRAPH_REPOSITORY_MODE", "postgres").lower()
    if mode != "postgres":
        raise ValueError("GRAPH_REPOSITORY_MODE must be postgres; demo graph data is disabled")
    if database_url is None:
        raise ValueError("DATABASE_URL is required when GRAPH_REPOSITORY_MODE=postgres")
    return PostgresGraphRepository(database_url)


def get_query_orchestrator() -> QueryOrchestrator:
    settings = get_settings()
    chat_responder: ChatResponder | None = None
    analysis_responder: AnalysisResponder | None = None
    if settings.intent_parser_mode == IntentParserMode.CLAUDE:
        chat_responder = ClaudeChatResponder(
            model=settings.claude_model,
            api_key=settings.anthropic_api_key,
            timeout_seconds=settings.claude_timeout_seconds,
        )
        analysis_responder = chat_responder
    return QueryOrchestrator(
        parser=get_intent_parser(),
        graph_repository=get_graph_repository(),
        chat_responder=chat_responder,
        analysis_responder=analysis_responder,
    )


def get_scenario_orchestrator() -> ScenarioOrchestrator:
    return ScenarioOrchestrator(graph_repository=get_graph_repository())
