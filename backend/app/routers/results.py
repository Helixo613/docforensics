from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas import AnalysisResult, ErrorResponse
from app.storage import sessions

router = APIRouter()


@router.get(
    "/results/{session_id}",
    response_model=AnalysisResult,
    responses={404: {"model": ErrorResponse}},
)
def get_results(session_id: str):
    session = sessions.get(session_id)
    if session is None:
        return JSONResponse(status_code=404, content={"error": "Session not found"})
    if session.results is None:
        return JSONResponse(status_code=404, content={"error": "Analysis not yet run"})
    return session.results

