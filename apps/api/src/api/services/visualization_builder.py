from api.schemas.common import VisualizationPayload
from causal_engine.models import CausalPath


class VisualizationBuilder:
    def build_for_paths(self, paths: list[CausalPath]) -> VisualizationPayload:
        highlighted_nodes: list[str] = []
        for path in paths:
            highlighted_nodes.extend(path.path)

        return VisualizationPayload(
            highlighted_nodes=list(dict.fromkeys(highlighted_nodes)),
            highlighted_edges=[],
            focus_subgraph_id="subgraph_vessel_a",
        )

