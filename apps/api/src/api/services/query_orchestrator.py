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
from math import prod
import re

import networkx as nx

from causal_engine.analysis import find_dominant_paths
from causal_engine.graph import to_networkx
from causal_engine.loops import detect_feedback_loops
from causal_engine.models import CausalPath, FcmGraph, FeedbackLoop
from llm_orchestrator.chat import AnalysisResponder, ChatResponder
from llm_orchestrator.models import IntentType, ScenarioIntervention as ParsedScenarioIntervention, StructuredQuery
from llm_orchestrator.parsers import IntentParser, IntentParserUnavailableError
from rag_engine.mock import InMemoryRetriever
from rag_engine.models import RetrievalQuery


MAX_REASONING_ITEMS = 5


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
        structured_query = _normalize_start_node_scenario_request(structured_query)
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
        requested_target_node_id = (
            structured_query.target.node_id
            if structured_query.target is not None
            and not _is_broad_scenario_effect_request(request.message, structured_query)
            else None
        )
        scenario = (
            self._run_scenario(request, structured_query, requested_target_node_id)
            if structured_query.intent == IntentType.SCENARIO_SIMULATION
            else None
        )
        target_node_id = (
            requested_target_node_id
            or _select_primary_scenario_outcome(scenario)
            if scenario is not None
            else structured_query.target.node_id if structured_query.target else "qc_productivity"
        )
        has_targeted_intervention = bool(
            scenario and requested_target_node_id and structured_query.intervention
        )
        paths = (
            _find_intervention_paths(
                graph=graph,
                intervention_node_id=structured_query.intervention.node_id,
                operation=structured_query.intervention.operation,
                value=structured_query.intervention.value,
                target_node_id=target_node_id,
            )
            if has_targeted_intervention and structured_query.intervention is not None
            else find_dominant_paths(
                graph,
                snapshot,
                target_node_id=target_node_id,
                max_paths=MAX_REASONING_ITEMS,
            )
        )
        loops = detect_feedback_loops(graph, snapshot, max_loops=MAX_REASONING_ITEMS)
        path_node_ids = {node_id for path in paths for node_id in path.path}
        visible_loops = (
            [loop for loop in loops if path_node_ids.intersection(loop.nodes)]
            if has_targeted_intervention
            else loops
        )
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
                for loop in visible_loops
            ],
        }
        evidence = _retrieve_evidence(
            message=request.message,
            terminal_id=request.terminal_id,
            target_node_id=target_node_id,
            path_node_ids=list(path_node_ids),
        )
        reasoning_trace = self._reasoning_trace_builder.build(
            graph=graph,
            target_node_id=target_node_id,
            paths=_top_reasoning_paths(paths),
            loops=_top_reasoning_loops(visible_loops),
            evidence=evidence,
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

    def _run_scenario(
        self,
        request: QueryRequest,
        structured_query: StructuredQuery,
        target_node_id: str | None,
    ) -> ScenarioResponse:
        intervention = (
            ScenarioInterventionRequest(**structured_query.intervention.model_dump())
            if structured_query.intervention is not None
            else _scenario_intervention(structured_query.raw_message)
        )
        return self._scenario_orchestrator.handle(
            ScenarioRequest(
                terminal_id=request.terminal_id,
                message=structured_query.raw_message,
                intervention=intervention,
                target_node_id=target_node_id,
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
    return sorted(loops, key=lambda loop: loop.strength, reverse=True)[:MAX_REASONING_ITEMS]


def _is_broad_scenario_effect_request(message: str, structured_query: StructuredQuery) -> bool:
    """Detect a request about a changed factor without a separately named outcome."""
    intervention = structured_query.intervention
    if intervention is None:
        return False
    if structured_query.target is not None and structured_query.target.node_id == intervention.node_id:
        return True

    normalized = re.sub(r"[?!.,]+$", "", message.strip().lower())
    source_label = intervention.node_id.replace("_", " ")
    patterns = (
        rf"(?:what(?: is|'s) )?(?:the )?effects? of (?:the )?{re.escape(source_label)}",
        rf"(?:what(?: is|'s) )?(?:the )?effects? of (?:an? |the )?(?:increase|decrease|rise|drop|reduction|improvement) (?:in|of) (?:the )?{re.escape(source_label)}",
        rf"what happens (?:if|when) (?:the )?{re.escape(source_label)}",
    )
    return any(re.fullmatch(pattern, normalized) is not None for pattern in patterns)


def _select_primary_scenario_outcome(scenario: ScenarioResponse) -> str:
    """Choose the largest modeled downstream effect for a broad scenario request."""
    intervention_node_ids = {
        intervention.get("node_id")
        for intervention in scenario.structured_intervention.get("interventions", [])
        if isinstance(intervention, dict) and isinstance(intervention.get("node_id"), str)
    }
    candidates = [
        (node_id, impact)
        for node_id, impact in scenario.predicted_impact.items()
        if node_id not in intervention_node_ids
    ]
    if not candidates:
        return next(iter(scenario.predicted_impact), "qc_productivity")
    return max(candidates, key=lambda item: (abs(item[1]), item[0]))[0]


def _find_intervention_paths(
    *,
    graph: FcmGraph,
    intervention_node_id: str,
    operation: str,
    value: float,
    target_node_id: str,
) -> list[CausalPath]:
    directed = to_networkx(graph)
    if intervention_node_id not in directed or target_node_id not in directed:
        return []

    signed_change = value if operation == "increase_relative" else -value
    candidates: list[CausalPath] = []
    for node_path in nx.all_simple_paths(
        directed,
        intervention_node_id,
        target_node_id,
        cutoff=8,
    ):
        weights = [
            float(directed[node_path[index]][node_path[index + 1]]["weight"])
            for index in range(len(node_path) - 1)
        ]
        confidences = [
            float(directed[node_path[index]][node_path[index + 1]]["confidence"])
            for index in range(len(node_path) - 1)
        ]
        candidates.append(
            CausalPath(
                path=list(node_path),
                contribution_ratio=abs(signed_change * prod(weights)),
                signed_impact=signed_change * prod(weights),
                confidence=prod(confidences),
            )
        )

    total = sum(path.contribution_ratio for path in candidates) or 1.0
    normalized = [
        path.model_copy(update={"contribution_ratio": path.contribution_ratio / total})
        for path in candidates
    ]
    return sorted(normalized, key=lambda path: path.contribution_ratio, reverse=True)[
        :MAX_REASONING_ITEMS
    ]


def _scenario_intervention(message: str) -> ScenarioInterventionRequest:
    lowered = message.lower()
    node_keywords = {
        "weather severity": "weather_severity",
        "weather": "weather_severity",
        "crane equipment availability": "crane_equipment_availability",
        "crane availability": "crane_equipment_availability",
        "qc productivity": "qc_productivity",
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


def _normalize_start_node_scenario_request(structured_query: StructuredQuery) -> StructuredQuery:
    """Guarantee simulation behavior when a user asks for the effects of a changed factor."""
    if not _is_start_node_scenario_message(structured_query.raw_message):
        return structured_query

    intervention = structured_query.intervention
    if intervention is None:
        inferred = _scenario_intervention(structured_query.raw_message)
        intervention = ParsedScenarioIntervention(
            node_id=inferred.node_id,
            operation=inferred.operation,
            value=inferred.value,
        )

    return structured_query.model_copy(
        update={
            "intent": IntentType.SCENARIO_SIMULATION,
            "intervention": intervention,
        }
    )


def _is_start_node_scenario_message(message: str) -> bool:
    normalized = re.sub(r"\s+", " ", message.strip().lower())
    return bool(
        re.match(r"^(?:what if|what happens (?:if|when))\b", normalized)
        or re.match(r"^(?:what(?: is|'s) )?(?:the )?effects? of\b", normalized)
        or re.match(r"^(?:what(?: is|'s) )?(?:the )?impact of\b", normalized)
    )


def _percentage_from_message(message: str) -> float:
    for token in message.replace("%", " %").split():
        if token.isdigit():
            value = int(token)
            if 0 < value <= 100:
                return value / 100
    return 0.15
