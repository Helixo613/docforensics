from __future__ import annotations

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from app.config import CONFIDENCE_THRESHOLD, SIMILARITY_THRESHOLD, TOP_K
from app.schemas import AnalysisResult, AnalyzeOverrides, ErrorResponse
from app.services.bucketing import build_result_payload
from app.services.candidate_generation import generate_candidate_pairs
from app.services.embeddings import build_embeddings
from app.services.nli import classify_candidate_pairs
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

    overrides_empty = overrides is None or (
        overrides.similarity_threshold is None
        and overrides.confidence_threshold is None
        and overrides.top_k is None
    )
    if overrides_empty and session.results is not None:
        return session.results

    similarity_threshold = (
        overrides.similarity_threshold
        if overrides and overrides.similarity_threshold is not None
        else SIMILARITY_THRESHOLD
    )
    confidence_threshold = (
        overrides.confidence_threshold
        if overrides and overrides.confidence_threshold is not None
        else CONFIDENCE_THRESHOLD
    )
    top_k = overrides.top_k if overrides and overrides.top_k is not None else TOP_K

    session.embeddings = build_embeddings(session.sentences)
    candidate_pairs = generate_candidate_pairs(
        session.embeddings,
        session.sentences,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
    )
    classified_pairs = classify_candidate_pairs(
        candidate_pairs,
        session.sentences,
        confidence_threshold=confidence_threshold,
    )
    session.results = build_result_payload(
        session,
        candidate_pairs=candidate_pairs,
        classified_pairs=classified_pairs,
    )
    return session.results
