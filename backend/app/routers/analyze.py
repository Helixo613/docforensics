from __future__ import annotations

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from app.schemas import AnalysisResult, AnalyzeOverrides, ErrorResponse
from app.services.pair_analysis import build_or_get_pair_analysis
from app.storage import sessions
from app.utils.model_loader import are_models_loaded

router = APIRouter()


@router.post(
    "/analyze/{session_id}",
    response_model=AnalysisResult,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def analyze_session(
    session_id: str,
    overrides: AnalyzeOverrides | None = Body(default=None),
):
    if not are_models_loaded():
        return JSONResponse(status_code=503, content={"error": "Models not loaded"})

    session = sessions.get(session_id)
    if session is None:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    return build_or_get_pair_analysis(session, overrides)
