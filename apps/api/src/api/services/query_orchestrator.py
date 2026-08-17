from api.schemas.query import QueryRequest, QueryResponse
from api.services.demo_data import build_demo_graph, build_demo_snapshot
from api.services.explanation_builder import ExplanationBuilder
from api.services.visualization_builder import VisualizationBuilder
from causal_engine.analysis import find_dominant_paths
from causal_engine.loops import detect_feedback_loops
from llm_orchestrator.parsers import MockIntentParser


class QueryOrchestrator:
    def __init__(self) -> None:
        self._parser = MockIntentParser()
        self._explanation_builder = ExplanationBuilder()
        self._visualization_builder = VisualizationBuilder()

    def handle(self, request: QueryRequest) -> QueryResponse:
        structured_query = self._parser.parse(request.message)
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
            "dominantPaths": [path.model_dump(by_alias=True) for path in paths],
            "feedbackLoops": [loop.model_dump(by_alias=True) for loop in loops],
        }
        evidence: list[dict[str, object]] = []

        return QueryResponse(
            analysis_id="analysis_demo_001",
            intent=structured_query.intent.value,
            answer=self._explanation_builder.build(causal_result, evidence),
            causal_result=causal_result,
            evidence=evidence,
            visualization=self._visualization_builder.build_for_paths(paths),
        )
