import os

import pytest
from llm_orchestrator.gemini_parser import GeminiIntentParser
from llm_orchestrator.models import IntentType


@pytest.mark.skipif(
    os.getenv("RUN_GEMINI_LIVE_TEST") != "1" or not os.getenv("GEMINI_API_KEY"),
    reason="set RUN_GEMINI_LIVE_TEST=1 and GEMINI_API_KEY to make a paid API request",
)
def test_gemini_parser_live_smoke() -> None:
    parser = GeminiIntentParser(
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
        model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        api_key=os.environ["GEMINI_API_KEY"],
    )

    query = parser.parse("What is driving vessel turnaround time?")

    assert query.intent == IntentType.ROOT_MECHANISM_ANALYSIS
    assert query.target is not None
    assert query.target.node_id == "vessel_turnaround_time"
