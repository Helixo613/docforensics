from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


IssueStatus = Literal["contested", "aligned", "mixed", "unclear"]
DocumentPositionLabel = Literal["side_0", "side_1", "mixed", "unclear"]
RelationType = Literal["agreement", "contradiction"]
IssueStructuralQuality = Literal["clean", "borderline", "weak"]
IssueLabelKind = Literal["representative_claim_excerpt"]


class V2ErrorResponse(BaseModel):
    error: str


class V2Claim(BaseModel):
    claim_id: str
    text: str
    doc_name: str
    page: int


class V2IssueRelation(BaseModel):
    relation: RelationType
    claim_ids: list[str]
    confidence: float


class V2IssueSide(BaseModel):
    side_id: Literal["side_0", "side_1"]
    documents: list[str]
    claims: list[V2Claim]


class V2DocumentPosition(BaseModel):
    doc_name: str
    position: DocumentPositionLabel
    claim_ids: list[str]


class V2Issue(BaseModel):
    issue_id: str
    status: IssueStatus
    label: str
    label_kind: IssueLabelKind
    label_claim_id: str
    structural_quality: IssueStructuralQuality
    merge_risk: bool
    documents_involved: list[str]
    sides: list[V2IssueSide]
    mixed_claims: list[V2Claim]
    unclear_claims: list[V2Claim]
    document_positions: list[V2DocumentPosition]
    relations: list[V2IssueRelation]


class V2IssueMapStats(BaseModel):
    total_issues: int
    total_claims: int
    contested_issues: int
    aligned_issues: int
    mixed_issues: int
    unclear_issues: int


class V2FallbackSignal(BaseModel):
    should_fallback: bool
    reasons: list[str]
    dominant_issue_share: float
    singleton_issue_ratio: float


class V2CoverageManifest(BaseModel):
    pair_derived_claims_total: int
    pair_derived_claims_represented_in_issues: int
    pair_relations_total: int
    pair_relations_represented_in_issues: int
    structurally_ambiguous_claims_in_issues: int
    uncorroborated_claims_outside_issue_map: int


class V2IssueMapResponse(BaseModel):
    session_id: str
    source: Literal["v1_pair_results"]
    stats: V2IssueMapStats
    coverage: V2CoverageManifest
    fallback: V2FallbackSignal
    issues: list[V2Issue]
