import os

from causal_engine.port_graph import build_reference_port_graph, build_reference_port_snapshot


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required to seed the graph database")

    from psycopg import connect

    graph = build_reference_port_graph()
    snapshot = build_reference_port_snapshot()
    with connect(database_url) as connection:
        connection.execute(
            "INSERT INTO terminals (id, name) VALUES (%s, %s) "
            "ON CONFLICT (id) DO NOTHING",
            (graph.terminal_id, "Terminal Alpha"),
        )
        connection.executemany(
            "INSERT INTO fcm_nodes (id, terminal_id, label, node_type, subsystem, entity_id) "
            "VALUES (%s, %s, %s, %s, %s, %s) "
            "ON CONFLICT (id) DO UPDATE SET label = EXCLUDED.label, "
            "node_type = EXCLUDED.node_type, subsystem = EXCLUDED.subsystem, "
            "entity_id = EXCLUDED.entity_id",
            [
                (
                    node.id,
                    graph.terminal_id,
                    node.label,
                    node.node_type.value,
                    node.subsystem,
                    node.entity_id,
                )
                for node in graph.nodes
            ],
        )
        connection.executemany(
            "INSERT INTO fcm_edges "
            "(id, terminal_id, source_node_id, target_node_id, base_weight, polarity, confidence, "
            "subsystem) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
            "ON CONFLICT (id) DO UPDATE SET base_weight = EXCLUDED.base_weight, "
            "polarity = EXCLUDED.polarity, confidence = EXCLUDED.confidence, "
            "subsystem = EXCLUDED.subsystem",
            [
                (
                    edge.id,
                    graph.terminal_id,
                    edge.source_node_id,
                    edge.target_node_id,
                    edge.base_weight,
                    edge.polarity.value,
                    edge.confidence,
                    edge.subsystem,
                )
                for edge in graph.edges
            ],
        )
        connection.execute(
            "INSERT INTO fcm_snapshots (id, terminal_id) VALUES (%s, %s) "
            "ON CONFLICT (id) DO NOTHING",
            (snapshot.snapshot_id, snapshot.terminal_id),
        )
        connection.execute(
            "DELETE FROM fcm_snapshot_values WHERE snapshot_id = %s",
            (snapshot.snapshot_id,),
        )
        connection.executemany(
            "INSERT INTO fcm_snapshot_values (snapshot_id, node_id, value) VALUES (%s, %s, %s)",
            [
                (snapshot.snapshot_id, node_id, value)
                for node_id, value in snapshot.node_values.items()
            ],
        )

    print(f"Seeded {len(graph.nodes)} nodes, {len(graph.edges)} edges, and one snapshot.")


if __name__ == "__main__":
    main()
