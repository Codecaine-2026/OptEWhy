from data_connectors.base import ConnectorHealth
from data_connectors.mock import MockTosConnector


def test_mock_connector_returns_current_state() -> None:
    connector = MockTosConnector()

    assert connector.health() == ConnectorHealth.OK
    assert connector.fetch_current_state("terminal_alpha")["terminal_id"] == "terminal_alpha"

