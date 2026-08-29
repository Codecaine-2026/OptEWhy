from typing import Any, Protocol

from api.services.demo_data import build_demo_graph, build_demo_snapshot
from causal_engine.models import EdgePolarity, FcmEdge, FcmGraph, FcmNode, FcmSnapshot, NodeType


class GraphRepository(Protocol):
    def get_graph(self, terminal_id: str) -> FcmGraph: ...

    def get_current_snapshot(self, terminal_id: str) -> FcmSnapshot: ...


class DemoGraphRepository:
    def get_graph(self, terminal_id: str) -> FcmGraph:
        graph = build_demo_graph()
        if graph.terminal_id != terminal_id:
            raise ValueError(f"Unknown terminal: {terminal_id}")
        return graph

    def get_current_snapshot(self, terminal_id: str) -> FcmSnapshot:
        snapshot = build_demo_snapshot()
        if snapshot.terminal_id != terminal_id:
            raise ValueError(f"Unknown terminal: {terminal_id}")
        return snapshot


class PostgresGraphRepository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def get_graph(self, terminal_id: str) -> FcmGraph:
        with self._connect() as connection:
            node_rows = connection.execute(
                "SELECT id, label, node_type, subsystem, entity_id "
                "FROM fcm_nodes WHERE terminal_id = %s ORDER BY id",
                (terminal_id,),
            ).fetchall()
            edge_rows = connection.execute(
                "SELECT id, source_node_id, target_node_id, base_weight, polarity, confidence, "
                "subsystem "
                "FROM fcm_edges WHERE terminal_id = %s ORDER BY id",
                (terminal_id,),
            ).fetchall()

        if not node_rows:
            raise ValueError(f"No graph data is available for terminal: {terminal_id}")
        return FcmGraph(
            id=f"graph_{terminal_id}_current",
            terminal_id=terminal_id,
            nodes=[
                FcmNode(
                    id=row[0],
                    label=row[1],
                    node_type=NodeType(row[2]),
                    subsystem=row[3],
                    entity_id=row[4],
                )
                for row in node_rows
            ],
            edges=[
                FcmEdge(
                    id=row[0],
                    source_node_id=row[1],
                    target_node_id=row[2],
                    base_weight=float(row[3]),
                    polarity=EdgePolarity(row[4]),
                    confidence=float(row[5]),
                    subsystem=row[6],
                )
                for row in edge_rows
            ],
        )

    def get_current_snapshot(self, terminal_id: str) -> FcmSnapshot:
        with self._connect() as connection:
            snapshot_row = connection.execute(
                "SELECT id FROM fcm_snapshots WHERE terminal_id = %s "
                "ORDER BY captured_at DESC LIMIT 1",
                (terminal_id,),
            ).fetchone()
            if snapshot_row is None:
                raise ValueError(f"No snapshot data is available for terminal: {terminal_id}")
            value_rows = connection.execute(
                "SELECT node_id, value FROM fcm_snapshot_values WHERE snapshot_id = %s",
                (snapshot_row[0],),
            ).fetchall()
        return FcmSnapshot(
            snapshot_id=snapshot_row[0],
            terminal_id=terminal_id,
            node_values={row[0]: float(row[1]) for row in value_rows},
        )

    def _connect(self) -> Any:
        from psycopg import connect

        return connect(self._database_url)
