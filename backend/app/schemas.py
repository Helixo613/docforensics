from __future__ import annotations

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str


class HealthResponse(BaseModel):
    status: str
    models_loaded: bool
    error: str | None = None


class DocumentSummary(BaseModel):
    name: str
    pages: int
    sentences: int


class UploadResponse(BaseModel):
    session_id: str
    documents: list[DocumentSummary]
    total_sentences: int


class AnalyzeOverrides(BaseModel):
    similarity_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    top_k: int | None = Field(default=None, ge=1)


class ClaimSource(BaseModel):
    text: str
    doc_name: str
    page: int


class PairResult(BaseModel):
    id: str
    claim_a: ClaimSource
    claim_b: ClaimSource
    confidence: float


class UncorroboratedResult(BaseModel):
    id: str
    claim: ClaimSource


class ResultStats(BaseModel):
    total_sentences: int
    candidate_pairs: int
    agreements_found: int
    contradictions_found: int
    uncorroborated_count: int


class AnalysisResult(BaseModel):
    session_id: str
    stats: ResultStats
    contradictions: list[PairResult]
    agreements: list[PairResult]
    uncorroborated: list[UncorroboratedResult]


class SearchResultItem(BaseModel):
    text: str
    doc_name: str
    page: int
    score: float


class SearchResponse(BaseModel):
    session_id: str
    query: str
    results: list[SearchResultItem]
