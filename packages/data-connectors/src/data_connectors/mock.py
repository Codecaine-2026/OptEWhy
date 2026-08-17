from data_connectors.base import ConnectorHealth, DataConnector


class MockTosConnector(DataConnector):
    def health(self) -> ConnectorHealth:
        return ConnectorHealth.OK

    def fetch_current_state(self, terminal_id: str) -> dict[str, object]:
        return {
            "terminal_id": terminal_id,
            "vessel_id": "vessel_a",
            "yard_density_block_b": 0.85,
            "qc_productivity": -0.15,
        }

