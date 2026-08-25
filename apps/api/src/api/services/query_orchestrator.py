from api.schemas.query import QueryRequest, QueryResponse
from api.services.demo_data import build_demo_graph, build_demo_snapshot
from api.services.explanation_builder import ExplanationBuilder
from api.services.reasoning_trace_builder import ReasoningTraceBuilder
from api.services.visualization_builder import VisualizationBuilder
from causal_engine.analysis import find_dominant_paths
from causal_engine.loops import detect_feedback_loops
from llm_orchestrator.chat import ChatResponder
from llm_orchestrator.models import IntentType
from llm_orchestrator.parsers import IntentParser


class QueryOrchestrator:
    def __init__(self, parser: IntentParser, chat_responder: ChatResponder | None = None) -> None:
        self._parser = parser
        self._chat_responder = chat_responder
        self._explanation_builder = ExplanationBuilder()
        self._reasoning_trace_builder = ReasoningTraceBuilder()
        self._visualization_builder = VisualizationBuilder()

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
                visualization=self._visualization_builder.build_for_paths([]),
            )

        graph = build_demo_graph()
        snapshot = build_demo_snapshot()
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
        evidence: list[dict[str, object]] = []
        reasoning_trace = self._reasoning_trace_builder.build(
            graph=graph,
            target_node_id=target_node_id,
            paths=paths,
            loops=loops,
            evidence=evidence,
        )

        return QueryResponse(
            analysis_id="analysis_demo_001",
            intent=structured_query.intent.value,
            answer=self._explanation_builder.build(causal_result, evidence),
            causal_result=causal_result,
            evidence=evidence,
            reasoning_trace=reasoning_trace,
            visualization=self._visualization_builder.build_for_trace(
                graph=graph,
                snapshot=snapshot,
                trace=reasoning_trace,
            ),
        )
