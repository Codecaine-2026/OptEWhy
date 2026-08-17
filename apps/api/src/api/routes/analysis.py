from api.schemas.query import AnalysisRecord
from fastapi import APIRouter

router = APIRouter(tags=["analysis"])


@router.get("/analysis/{analysis_id}", response_model=AnalysisRecord)
def get_analysis(analysis_id: str) -> AnalysisRecord:
    return AnalysisRecord(
        analysis_id=analysis_id,
        terminal_id="terminal_alpha",
        request="Why is Vessel A productivity low?",
        snapshot_id="snap_current_shift_demo",
        fcm_model_version="fcm_demo_v0.1.0",
        created_at="2026-08-18T09:12:00+09:00",
    )

