import os

import pytest
from llm_orchestrator.models import IntentType
from llm_orchestrator.openai_parser import OpenAIIntentParser


@pytest.mark.skipif(
    os.getenv("RUN_OPENAI_LIVE_TEST") != "1" or not os.getenv("OPENAI_API_KEY"),
    reason="set RUN_OPENAI_LIVE_TEST=1 and OPENAI_API_KEY to make a paid API request",
)
def test_openai_parser_live_smoke() -> None:
    parser = OpenAIIntentParser(
        node_catalog={
            "weather_severity": "Weather Severity",
            "vessel_arrival_delay": "Vessel Arrival Delay",
            "berth_occupancy": "Berth Occupancy",
            "yard_density": "Yard Density",
            "truck_travel_time": "Internal Truck Travel Time",
            "qc_waiting": "QC Waiting",
            "qc_productivity": "QC Productivity",
            "vessel_turnaround_time": "Vessel Turnaround Time",
        },
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        api_key=os.environ["OPENAI_API_KEY"],
    )

    query = parser.parse("What is driving vessel turnaround time?")

    assert query.intent == IntentType.ROOT_MECHANISM_ANALYSIS
    assert query.target is not None
    assert query.target.node_id == "vessel_turnaround_time"
