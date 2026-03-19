from __future__ import annotations

from app.config import CONFIDENCE_THRESHOLD, SIMILARITY_THRESHOLD, TOP_K
from app.schemas import AnalyzeOverrides
from app.services.bucketing import build_result_payload
from app.services.candidate_generation import generate_candidate_pairs
from app.services.embeddings import build_embeddings
from app.services.nli import classify_candidate_pairs
from app.storage import Session


def _overrides_empty(overrides: AnalyzeOverrides | None) -> bool:
    return overrides is None or (
        overrides.similarity_threshold is None
        and overrides.confidence_threshold is None
        and overrides.top_k is None
    )


def build_or_get_pair_analysis(
    session: Session,
    overrides: AnalyzeOverrides | None = None,
) -> dict:
    if _overrides_empty(overrides) and session.results is not None:
        return session.results

    # V2 is a downstream read-only view over pair results. Any fresh V1 analysis
    # invalidates the derived V2 cache before recomputing the pair payload.
    session.v2_results = None
    session.v2_source_signature = None

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
