from __future__ import annotations

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from app.schemas import AnalyzeOverrides, ErrorResponse
from app.services.pair_analysis import build_or_get_pair_analysis
from app.services.v2_issue_map import build_issue_map, build_pair_relation_signature
from app.storage import sessions
from app.utils.model_loader import are_models_loaded
from app.v2_schemas import V2ErrorResponse, V2IssueMapResponse

router = APIRouter()


def _overrides_empty(overrides: AnalyzeOverrides | None) -> bool:
    return overrides is None or (
        overrides.similarity_threshold is None
        and overrides.confidence_threshold is None
        and overrides.top_k is None
    )


def _invalidate_stale_v2_cache(session) -> None:
    if session.v2_results is None or session.results is None:
        return

    current_signature = build_pair_relation_signature(session.results)
    if session.v2_source_signature != current_signature:
        session.v2_results = None
        session.v2_source_signature = None


@router.post(
    "/v2/analyze/{session_id}",
    response_model=V2IssueMapResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def analyze_session_v2(
    session_id: str,
    overrides: AnalyzeOverrides | None = Body(default=None),
):
    session = sessions.get(session_id)
    if session is None:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    _invalidate_stale_v2_cache(session)

    if _overrides_empty(overrides) and session.v2_results is not None:
        return session.v2_results

    if _overrides_empty(overrides) and session.results is not None:
        pair_results = session.results
    else:
        if not are_models_loaded():
            return JSONResponse(status_code=503, content={"error": "Models not loaded"})
        pair_results = build_or_get_pair_analysis(session, overrides)

    session.v2_results = build_issue_map(pair_results)
    session.v2_source_signature = build_pair_relation_signature(pair_results)
    return session.v2_results


@router.get(
    "/v2/results/{session_id}",
    response_model=V2IssueMapResponse,
    responses={404: {"model": V2ErrorResponse}},
)
def get_v2_results(session_id: str):
    session = sessions.get(session_id)
    if session is None:
        return JSONResponse(status_code=404, content={"error": "Session not found"})

    _invalidate_stale_v2_cache(session)

    if session.v2_results is None:
        return JSONResponse(status_code=404, content={"error": "V2 analysis not yet run"})
    return session.v2_results
