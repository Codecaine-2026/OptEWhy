from api.schemas.common import ReasoningTracePayload, VisualizationPayload
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
                reasoning_trace=ReasoningTracePayload(target_node_id=""),
                visualization=VisualizationPayload(),
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
        evidence: list[dict[str, object]] = [
            {
                "documentId": "shift_report_block_b_001",
                "sourceTitle": "Shift Handover Log #402 (Yard Block B)",
                "subsystem": "yard",
                "text": "07:15 - RTG-02 mechanical fault led to 25min container retrieval backlog and internal truck queuing at Block B.",
                "score": 0.94,
            },
            {
                "documentId": "maintenance_qc4_demo",
                "sourceTitle": "Quay Crane Maintenance Notice #118",
                "subsystem": "quay",
                "text": "QC4 operating at normal capacity; delays observed were downstream from internal transport arrivals rather than crane mechanics.",
                "score": 0.88,
            },
        ]
        reasoning_trace = self._reasoning_trace_builder.build(
            graph=graph,
            target_node_id=target_node_id,
            paths=paths,
            loops=loops,
            evidence=evidence,
        )

        if structured_query.intent == IntentType.SCENARIO_SIMULATION:
            answer = (
                "Simulated Intervention: Reallocating 15% container load from Yard Block B to Block D "
                "reduces Yard Density from 85% to 72% (-13%). This alleviates Internal Truck Travel Time (-6%) "
                "and QC Waiting (-4%), yielding a +3.7% boost in QC Productivity (+1.0 mph) and saving 19 minutes "
                "on Vessel Turnaround.\n\n"
                "⚠️ Tradeoff Notice: Block D density increase introduces a +2.0% Gate Retrieval Delay during peak hours."
            )
            analysis_id = "scenario_demo_001"
        elif structured_query.intent == IntentType.ROOT_MECHANISM_ANALYSIS:
            answer = (
                "Root Mechanism Analysis: High Yard Density (85%) triggers a reinforcing feedback loop "
                "with Yard Rehandle Rate and Internal Truck Travel Time. Internal transport delays starve Quay Cranes "
                "of container flow, causing 18 min average QC waiting and dragging down gross moves per hour."
            )
            analysis_id = "mechanism_demo_001"
        else:
            answer = self._explanation_builder.build(causal_result, evidence)
            analysis_id = "analysis_demo_001"

        return QueryResponse(
            analysis_id=analysis_id,
            intent=structured_query.intent.value,
            answer=answer,
            causal_result=causal_result,
            evidence=evidence,
            reasoning_trace=reasoning_trace,
            visualization=self._visualization_builder.build_for_trace(
                graph=graph,
                snapshot=snapshot,
                trace=reasoning_trace,
            ),
        )

