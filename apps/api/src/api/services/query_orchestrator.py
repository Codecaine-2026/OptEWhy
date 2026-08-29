from api.schemas.common import ReasoningTracePayload, VisualizationPayload
from api.schemas.query import (
    QueryRequest,
    QueryResponse,
    ScenarioInterventionRequest,
    ScenarioRequest,
    ScenarioResponse,
)
from api.services.evidence_seed import load_rag_seed_chunks
from api.services.graph_repository import DemoGraphRepository, GraphRepository
from api.services.reasoning_trace_builder import ReasoningTraceBuilder
from api.services.scenario_orchestrator import ScenarioOrchestrator
from api.services.visualization_builder import VisualizationBuilder
from causal_engine.analysis import find_dominant_paths
from causal_engine.loops import detect_feedback_loops
from causal_engine.models import CausalPath, FeedbackLoop
from llm_orchestrator.chat import AnalysisResponder, ChatResponder
from llm_orchestrator.models import IntentType
from llm_orchestrator.parsers import IntentParser, IntentParserUnavailableError
from rag_engine.mock import InMemoryRetriever
from rag_engine.models import RetrievalQuery


class QueryOrchestrator:
    def __init__(
        self,
        parser: IntentParser,
        graph_repository: GraphRepository | None = None,
        chat_responder: ChatResponder | None = None,
        analysis_responder: AnalysisResponder | None = None,
    ) -> None:
        self._parser = parser
        self._graph_repository = graph_repository or DemoGraphRepository()
        self._chat_responder = chat_responder
        self._analysis_responder = analysis_responder
        self._reasoning_trace_builder = ReasoningTraceBuilder()
        self._visualization_builder = VisualizationBuilder()
        self._scenario_orchestrator = ScenarioOrchestrator(self._graph_repository)

    def handle(self, request: QueryRequest) -> QueryResponse:
        structured_query = self._parser.parse(request.message)
        if structured_query.intent == IntentType.CASUAL_CONVERSATION:
            answer = (
                self._chat_responder.respond(request.message)
                if self._chat_responder is not None
                else (
                    "Hi! I’m the OptEWhy Copilot. Ask me about port operations "
                    "or the causal graph."
                )
            )
            return QueryResponse(
                analysis_id="chat_demo_001",
                intent=structured_query.intent.value,
                answer=answer,
                causal_result={},
                evidence=[],
                reasoning_trace=ReasoningTracePayload(target_node_id=""),
                visualization=VisualizationPayload(),
            )

        graph = self._graph_repository.get_graph(request.terminal_id)
        snapshot = self._graph_repository.get_current_snapshot(request.terminal_id)
        target_node_id = (
            structured_query.target.node_id if structured_query.target else "qc_productivity"
        )
        paths = find_dominant_paths(graph, snapshot, target_node_id=target_node_id)
        loops = detect_feedback_loops(graph, snapshot)
        causal_result: dict[str, object] = {
            "targetNodeId": target_node_id,
            "observedDelta": snapshot.node_values.get(target_node_id, 0.0),
            "dominantPaths": [
                {
                    "path": path.path,
                    "contributionRatio": path.contribution_ratio,
                    "signedImpact": path.signed_impact,
                    "confidence": path.confidence,
                }
                for path in paths
            ],
            "feedbackLoops": [
                {
                    "nodes": loop.nodes,
                    "loopType": loop.loop_type,
                    "strength": loop.strength,
                    "confidence": loop.confidence,
                }
                for loop in loops
            ],
        }
        evidence = _retrieve_evidence(
            message=request.message,
            terminal_id=request.terminal_id,
            target_node_id=target_node_id,
            path_node_ids=[node_id for path in paths for node_id in path.path],
        )
        reasoning_trace = self._reasoning_trace_builder.build(
            graph=graph,
            target_node_id=target_node_id,
            paths=_top_reasoning_paths(paths),
            loops=_top_reasoning_loops(loops),
            evidence=evidence,
        )
        scenario = (
            self._run_scenario(request, structured_query.raw_message)
            if structured_query.intent == IntentType.SCENARIO_SIMULATION
            else None
        )

        return QueryResponse(
            analysis_id="analysis_demo_001",
            intent=structured_query.intent.value,
            answer=self._build_analysis_answer(
                message=request.message,
                causal_result=causal_result,
                evidence=evidence,
                scenario=scenario,
            ),
            causal_result=causal_result,
            evidence=evidence,
            reasoning_trace=reasoning_trace,
            visualization=self._visualization_builder.build_for_trace(
                graph=graph,
                snapshot=snapshot,
                trace=reasoning_trace,
            ),
            scenario=scenario,
        )

    def _build_analysis_answer(
        self,
        *,
        message: str,
        causal_result: dict[str, object],
        evidence: list[dict[str, object]],
        scenario: ScenarioResponse | None,
    ) -> str:
        if self._analysis_responder is None:
            raise IntentParserUnavailableError("Claude analysis responder is not configured")
        return self._analysis_responder.respond_to_analysis(
            message=message,
            causal_result=causal_result,
            evidence=evidence,
            scenario=scenario.model_dump() if scenario is not None else None,
        )

    def _run_scenario(self, request: QueryRequest, message: str) -> ScenarioResponse:
        intervention = _scenario_intervention(message)
        return self._scenario_orchestrator.handle(
            ScenarioRequest(
                terminal_id=request.terminal_id,
                message=message,
                intervention=intervention,
            )
        )


def _retrieve_evidence(
    *,
    message: str,
    terminal_id: str,
    target_node_id: str,
    path_node_ids: list[str],
) -> list[dict[str, object]]:
    retriever = InMemoryRetriever(list(load_rag_seed_chunks()))
    entity_ids = list(dict.fromkeys([target_node_id, *path_node_ids]))
    results = retriever.retrieve(
        RetrievalQuery(
            question=message,
            terminal_id=terminal_id,
            entity_ids=entity_ids,
            limit=3,
        )
    )
    return [
        {
            "documentId": result.citation.document_id,
            "chunkId": result.citation.chunk_id,
            "sourceTitle": result.metadata.source_title,
            "sourceUrl": result.metadata.source_url,
            "text": result.text,
            "score": result.citation.score,
            "relatedNodes": result.metadata.related_nodes,
            "relatedEdges": result.metadata.related_edges,
        }
        for result in results
    ]


def _top_reasoning_paths(paths: list[CausalPath]) -> list[CausalPath]:
    return sorted(paths, key=lambda path: path.contribution_ratio, reverse=True)[:1]


def _top_reasoning_loops(loops: list[FeedbackLoop]) -> list[FeedbackLoop]:
    return sorted(loops, key=lambda loop: loop.strength, reverse=True)[:3]


def _scenario_intervention(message: str) -> ScenarioInterventionRequest:
    lowered = message.lower()
    node_keywords = {
        "yard density": "yard_density",
        "야드 밀도": "yard_density",
        "truck travel": "truck_travel_time",
        "트럭 이동": "truck_travel_time",
        "qc waiting": "qc_waiting",
        "qc 대기": "qc_waiting",
        "berth occupancy": "berth_occupancy",
        "선석 점유": "berth_occupancy",
    }
    node_id = next(
        (candidate for phrase, candidate in node_keywords.items() if phrase in lowered),
        "yard_density",
    )
    percentage = _percentage_from_message(lowered)
    operation = (
        "decrease_relative"
        if any(
            word in lowered
            for word in ("decrease", "reduce", "lower", "improve", "낮", "줄", "개선")
        )
        else "increase_relative"
    )
    return ScenarioInterventionRequest(node_id=node_id, operation=operation, value=percentage)


def _percentage_from_message(message: str) -> float:
    for token in message.replace("%", " %").split():
        if token.isdigit():
            value = int(token)
            if 0 < value <= 100:
                return value / 100
    return 0.15
