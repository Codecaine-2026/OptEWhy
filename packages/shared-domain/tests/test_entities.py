from shared_domain.entities import Terminal
from shared_domain.metrics import NormalizedNodeValue


def test_terminal_defaults_timezone() -> None:
    terminal = Terminal(id="terminal_alpha", name="Terminal Alpha")

    assert terminal.timezone == "Asia/Seoul"


def test_normalized_node_value_bounds() -> None:
    value = NormalizedNodeValue(node_id="yard_density", value=0.85)

    assert value.value == 0.85

