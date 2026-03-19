from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.schemas import ErrorResponse, SearchResponse
from app.services.search import search_session_sentences
from app.storage import sessions
from app.utils.model_loader import are_models_loaded

router = APIRouter()


@router.get(
    "/search/{session_id}",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def search_session(
    session_id: str,
    q: str | None = Query(default=None),
):
    if not are_models_loaded():
        return JSONResponse(status_code=503, content={"error": "Models not loaded"})

    session = sessions.get(session_id)
    if session is None:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    query = (q or "").strip()
    if not query:
        return JSONResponse(status_code=400, content={"error": "Query cannot be blank"})

    try:
        return search_session_sentences(session, query)
    except ValueError as exc:
        return JSONResponse(status_code=409, content={"error": str(exc)})
