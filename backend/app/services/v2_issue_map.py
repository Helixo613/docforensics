from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class RegistryClaim:
    claim_id: str
    text: str
    doc_name: str
    page: int


@dataclass(frozen=True)
class RegistryRelation:
    relation: str
    left_id: str
    right_id: str
    confidence: float


class _UnionFind:
    def __init__(self, items: list[str]):
        self.parents = {item: item for item in items}

    def find(self, item: str) -> str:
        parent = self.parents[item]
        if parent != item:
            self.parents[item] = self.find(parent)
        return self.parents[item]

    def union(self, left: str, right: str) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parents[right_root] = left_root


def _claim_key(payload: dict) -> tuple[str, str, int]:
    return (
        payload["text"],
        payload["doc_name"],
        int(payload["page"]),
    )


def _truncate_label(text: str, limit: int = 140) -> str:
    stripped = " ".join(text.split())
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[: limit - 3].rstrip()}..."


def _canonicalize_claim_payload(payload: dict) -> dict:
    return {
        "text": payload["text"],
        "doc_name": payload["doc_name"],
        "page": int(payload["page"]),
    }


def _canonicalize_pair_item(pair: dict) -> dict:
    left_claim = _canonicalize_claim_payload(pair["claim_a"])
    right_claim = _canonicalize_claim_payload(pair["claim_b"])
    ordered_claims = sorted(
        [left_claim, right_claim],
        key=lambda claim: (claim["doc_name"], claim["page"], claim["text"]),
    )
    return {
        "claims": ordered_claims,
        "confidence": round(float(pair["confidence"]), 2),
    }


def build_pair_relation_signature(pair_results: dict) -> str:
    relevant_payload = {
        "agreements": sorted(
            (
                _canonicalize_pair_item(pair)
                for pair in pair_results.get("agreements", [])
            ),
            key=lambda pair: (
                pair["claims"][0]["doc_name"],
                pair["claims"][0]["page"],
                pair["claims"][0]["text"],
                pair["claims"][1]["doc_name"],
                pair["claims"][1]["page"],
                pair["claims"][1]["text"],
                pair["confidence"],
            ),
        ),
        "contradictions": sorted(
            (
                _canonicalize_pair_item(pair)
                for pair in pair_results.get("contradictions", [])
            ),
            key=lambda pair: (
                pair["claims"][0]["doc_name"],
                pair["claims"][0]["page"],
                pair["claims"][0]["text"],
                pair["claims"][1]["doc_name"],
                pair["claims"][1]["page"],
                pair["claims"][1]["text"],
                pair["confidence"],
            ),
        ),
    }
    return json.dumps(relevant_payload, sort_keys=True, separators=(",", ":"))


def build_claim_registry(pair_results: dict) -> tuple[dict[str, RegistryClaim], list[RegistryRelation]]:
    claims: dict[str, RegistryClaim] = {}
    claim_ids_by_key: dict[tuple[str, str, int], str] = {}
    relations: list[RegistryRelation] = []

    def ensure_claim(payload: dict) -> str:
        key = _claim_key(payload)
        existing = claim_ids_by_key.get(key)
        if existing is not None:
            return existing

        claim_id = f"cl_{len(claims)}"
        claim = RegistryClaim(
            claim_id=claim_id,
            text=payload["text"],
            doc_name=payload["doc_name"],
            page=int(payload["page"]),
        )
        claim_ids_by_key[key] = claim_id
        claims[claim_id] = claim
        return claim_id

    for relation_name, pair_key in (("agreement", "agreements"), ("contradiction", "contradictions")):
        for pair in pair_results.get(pair_key, []):
            left_id = ensure_claim(pair["claim_a"])
            right_id = ensure_claim(pair["claim_b"])
            relations.append(
                RegistryRelation(
                    relation=relation_name,
                    left_id=left_id,
                    right_id=right_id,
                    confidence=round(float(pair["confidence"]), 2),
                )
            )

    return claims, relations


def group_claims_by_relation_components(
    claims: dict[str, RegistryClaim],
    relations: list[RegistryRelation],
) -> list[list[str]]:
    adjacency: dict[str, set[str]] = {claim_id: set() for claim_id in claims}
    for relation in relations:
        adjacency[relation.left_id].add(relation.right_id)
        adjacency[relation.right_id].add(relation.left_id)

    remaining = set(claims)
    components: list[list[str]] = []
    while remaining:
        start = min(remaining)
        stack = [start]
        component: list[str] = []
        remaining.remove(start)

        while stack:
            claim_id = stack.pop()
            component.append(claim_id)
            for neighbor in sorted(adjacency[claim_id]):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    stack.append(neighbor)

        components.append(sorted(component))

    components.sort(key=lambda component: (-len(component), component[0]))
    return components


def resolve_issue_sides(
    component_claim_ids: list[str],
    relations: list[RegistryRelation],
) -> dict[str, list[str]]:
    issue_claims = set(component_claim_ids)
    issue_relations = [
        relation
        for relation in relations
        if relation.left_id in issue_claims and relation.right_id in issue_claims
    ]
    if not issue_relations:
        return {"side_0": [], "side_1": [], "mixed": [], "unclear": sorted(component_claim_ids)}

    union_find = _UnionFind(component_claim_ids)
    for relation in issue_relations:
        if relation.relation == "agreement":
            union_find.union(relation.left_id, relation.right_id)

    blocks: dict[str, list[str]] = defaultdict(list)
    for claim_id in component_claim_ids:
        blocks[union_find.find(claim_id)].append(claim_id)

    contradiction_graph: dict[str, set[str]] = {root: set() for root in blocks}
    for relation in issue_relations:
        if relation.relation != "contradiction":
            continue
        left_root = union_find.find(relation.left_id)
        right_root = union_find.find(relation.right_id)
        if left_root == right_root:
            return {
                "side_0": [],
                "side_1": [],
                "mixed": sorted(component_claim_ids),
                "unclear": [],
            }
        contradiction_graph[left_root].add(right_root)
        contradiction_graph[right_root].add(left_root)

    if not any(contradiction_graph.values()):
        only_block = sorted(blocks)[0]
        return {
            "side_0": sorted(blocks[only_block]),
            "side_1": [],
            "mixed": [],
            "unclear": [],
        }

    colors: dict[str, int] = {}
    for root in sorted(blocks):
        if root in colors:
            continue
        if not contradiction_graph[root]:
            colors[root] = 0
            continue

        colors[root] = 0
        queue = [root]
        while queue:
            current = queue.pop(0)
            for neighbor in sorted(contradiction_graph[current]):
                expected = 1 - colors[current]
                current_color = colors.get(neighbor)
                if current_color is None:
                    colors[neighbor] = expected
                    queue.append(neighbor)
                    continue
                if current_color != expected:
                    return {
                        "side_0": [],
                        "side_1": [],
                        "mixed": sorted(component_claim_ids),
                        "unclear": [],
                    }

    sides = {"side_0": [], "side_1": [], "mixed": [], "unclear": []}
    for root, claim_ids in blocks.items():
        ordered_claim_ids = sorted(claim_ids)
        color = colors.get(root)
        if color == 0:
            sides["side_0"].extend(ordered_claim_ids)
        elif color == 1:
            sides["side_1"].extend(ordered_claim_ids)
        else:
            sides["unclear"].extend(ordered_claim_ids)

    for key in sides:
        sides[key] = sorted(sides[key])
    return sides


def resolve_issue_status(
    sides: dict[str, list[str]],
    relations: list[RegistryRelation],
) -> str:
    has_contradictions = any(relation.relation == "contradiction" for relation in relations)
    has_agreements = any(relation.relation == "agreement" for relation in relations)
    resolved_side_count = int(bool(sides["side_0"])) + int(bool(sides["side_1"]))
    has_ambiguous_material = bool(sides["mixed"] or sides["unclear"])

    if has_contradictions:
        if resolved_side_count >= 2 and not has_ambiguous_material:
            return "contested"
        return "mixed" if any(sides.values()) else "unclear"

    if has_agreements:
        if resolved_side_count == 1 and not has_ambiguous_material:
            return "aligned"
        return "mixed"

    return "unclear"


def _build_document_positions(
    claims: dict[str, RegistryClaim],
    sides: dict[str, list[str]],
) -> list[dict]:
    claim_positions: dict[str, str] = {}
    for position, claim_ids in sides.items():
        for claim_id in claim_ids:
            claim_positions[claim_id] = position

    claims_by_doc: dict[str, list[str]] = defaultdict(list)
    for claim_id, claim in claims.items():
        claims_by_doc[claim.doc_name].append(claim_id)

    positions: list[dict] = []
    for doc_name in sorted(claims_by_doc):
        doc_claim_ids = sorted(claims_by_doc[doc_name])
        bucket_set = {claim_positions[claim_id] for claim_id in doc_claim_ids}
        if "mixed" in bucket_set:
            position = "mixed"
        elif "side_0" in bucket_set and "side_1" in bucket_set:
            position = "mixed"
        elif "unclear" in bucket_set and ("side_0" in bucket_set or "side_1" in bucket_set):
            position = "mixed"
        elif "side_0" in bucket_set:
            position = "side_0"
        elif "side_1" in bucket_set:
            position = "side_1"
        else:
            position = "unclear"

        positions.append(
            {
                "doc_name": doc_name,
                "position": position,
                "claim_ids": doc_claim_ids,
            }
        )

    return positions


def _issue_claim_count(issue: dict) -> int:
    return (
        sum(len(side["claims"]) for side in issue["sides"])
        + len(issue["mixed_claims"])
        + len(issue["unclear_claims"])
    )


def _resolve_merge_risk(
    claim_count: int,
    relation_count: int,
) -> bool:
    return claim_count >= 5 and relation_count <= claim_count


def _resolve_structural_quality(issue: dict) -> str:
    claim_count = _issue_claim_count(issue)
    relation_count = len(issue["relations"])
    ambiguous_claim_count = len(issue["mixed_claims"]) + len(issue["unclear_claims"])
    mixed_document_positions = sum(
        1 for position in issue["document_positions"] if position["position"] == "mixed"
    )

    if claim_count == 0 or relation_count == 0:
        return "weak"
    if issue["status"] == "unclear" or len(issue["sides"]) == 0:
        return "weak"
    if (
        ambiguous_claim_count == 0
        and mixed_document_positions == 0
        and not issue["merge_risk"]
        and issue["status"] in {"contested", "aligned"}
    ):
        return "clean"
    return "borderline"


def _build_issue(
    issue_index: int,
    component_claim_ids: list[str],
    all_claims: dict[str, RegistryClaim],
    all_relations: list[RegistryRelation],
) -> dict:
    issue_claim_lookup = {claim_id: all_claims[claim_id] for claim_id in component_claim_ids}
    issue_relations = [
        relation
        for relation in all_relations
        if relation.left_id in issue_claim_lookup and relation.right_id in issue_claim_lookup
    ]
    sides = resolve_issue_sides(component_claim_ids, issue_relations)

    degree_by_claim = {claim_id: 0 for claim_id in component_claim_ids}
    for relation in issue_relations:
        degree_by_claim[relation.left_id] += 1
        degree_by_claim[relation.right_id] += 1

    representative_claim_id = min(
        component_claim_ids,
        key=lambda claim_id: (-degree_by_claim[claim_id], claim_id),
    )
    representative_claim = issue_claim_lookup[representative_claim_id]

    def build_claim_list(claim_ids: list[str]) -> list[dict]:
        return [
            {
                "claim_id": claim_id,
                "text": issue_claim_lookup[claim_id].text,
                "doc_name": issue_claim_lookup[claim_id].doc_name,
                "page": issue_claim_lookup[claim_id].page,
            }
            for claim_id in sorted(claim_ids)
        ]

    merge_risk = _resolve_merge_risk(
        claim_count=len(component_claim_ids),
        relation_count=len(issue_relations),
    )
    issue_payload = {
        "issue_id": f"issue_{issue_index}",
        "label": _truncate_label(representative_claim.text),
        "label_kind": "representative_claim_excerpt",
        "label_claim_id": representative_claim_id,
        "merge_risk": merge_risk,
        "documents_involved": sorted({claim.doc_name for claim in issue_claim_lookup.values()}),
        "sides": [
            {
                "side_id": side_id,
                "documents": sorted({issue_claim_lookup[claim_id].doc_name for claim_id in claim_ids}),
                "claims": build_claim_list(claim_ids),
            }
            for side_id in ("side_0", "side_1")
            if sides[side_id]
            for claim_ids in [sides[side_id]]
        ],
        "mixed_claims": build_claim_list(sides["mixed"]),
        "unclear_claims": build_claim_list(sides["unclear"]),
        "document_positions": _build_document_positions(issue_claim_lookup, sides),
        "relations": [
            {
                "relation": relation.relation,
                "claim_ids": [relation.left_id, relation.right_id],
                "confidence": relation.confidence,
            }
            for relation in sorted(
                issue_relations,
                key=lambda relation: (
                    relation.relation,
                    relation.left_id,
                    relation.right_id,
                ),
            )
        ],
    }
    status = resolve_issue_status(sides, issue_relations)
    if any(item["position"] == "mixed" for item in issue_payload["document_positions"]) and status != "unclear":
        issue_payload["status"] = "mixed"
    else:
        issue_payload["status"] = status
    issue_payload["structural_quality"] = _resolve_structural_quality(issue_payload)
    return issue_payload


def evaluate_issue_map_quality(issues: list[dict]) -> dict:
    total_claims = sum(_issue_claim_count(issue) for issue in issues)
    total_issues = len(issues)
    dominant_issue_share = round(
        max(
            (
                (
                    sum(len(side["claims"]) for side in issue["sides"])
                    + len(issue["mixed_claims"])
                    + len(issue["unclear_claims"])
                )
                / total_claims
            )
            for issue in issues
        ),
        2,
    ) if total_claims else 0.0
    singleton_issues = 0
    resolved_issues = 0
    unclear_issues = 0
    for issue in issues:
        claim_count = _issue_claim_count(issue)
        if claim_count == 1:
            singleton_issues += 1
        if issue["status"] == "unclear":
            unclear_issues += 1
        else:
            resolved_issues += 1

    singleton_issue_ratio = round(singleton_issues / total_issues, 2) if total_issues else 0.0

    reasons: list[str] = []
    if not issues:
        reasons.append("no_issue_structure")
    if issues and unclear_issues == total_issues:
        reasons.append("all_issues_unclear")
    if total_issues >= 4 and singleton_issue_ratio >= 0.75:
        reasons.append("mostly_singleton_issues")
    if total_issues == 1 and total_claims >= 5 and issues[0]["status"] in {"mixed", "unclear"}:
        reasons.append("single_incoherent_issue")
    if dominant_issue_share >= 0.9 and total_claims >= 8 and resolved_issues <= 1:
        reasons.append("single_dominant_issue")

    return {
        "should_fallback": bool(reasons),
        "reasons": reasons,
        "dominant_issue_share": dominant_issue_share,
        "singleton_issue_ratio": singleton_issue_ratio,
    }


def build_coverage_manifest(
    pair_results: dict,
    issues: list[dict],
    pair_claim_count: int,
    relation_count: int,
) -> dict:
    return {
        "pair_derived_claims_total": pair_claim_count,
        "pair_derived_claims_represented_in_issues": sum(_issue_claim_count(issue) for issue in issues),
        "pair_relations_total": relation_count,
        "pair_relations_represented_in_issues": sum(len(issue["relations"]) for issue in issues),
        "structurally_ambiguous_claims_in_issues": sum(
            len(issue["mixed_claims"]) + len(issue["unclear_claims"])
            for issue in issues
        ),
        "uncorroborated_claims_outside_issue_map": len(pair_results.get("uncorroborated", [])),
    }


def build_issue_map(pair_results: dict) -> dict:
    claims, relations = build_claim_registry(pair_results)
    issue_components = group_claims_by_relation_components(claims, relations)
    issues = [
        _build_issue(issue_index, component, claims, relations)
        for issue_index, component in enumerate(issue_components)
    ]
    issues.sort(
        key=lambda issue: (
            -(
                sum(len(side["claims"]) for side in issue["sides"])
                + len(issue["mixed_claims"])
                + len(issue["unclear_claims"])
            ),
            issue["issue_id"],
        )
    )

    fallback = evaluate_issue_map_quality(issues)
    coverage = build_coverage_manifest(
        pair_results=pair_results,
        issues=issues,
        pair_claim_count=len(claims),
        relation_count=len(relations),
    )
    status_counts = defaultdict(int)
    for issue in issues:
        status_counts[issue["status"]] += 1

    return {
        "session_id": pair_results["session_id"],
        "source": "v1_pair_results",
        "stats": {
            "total_issues": len(issues),
            "total_claims": len(claims),
            "contested_issues": status_counts["contested"],
            "aligned_issues": status_counts["aligned"],
            "mixed_issues": status_counts["mixed"],
            "unclear_issues": status_counts["unclear"],
        },
        "coverage": coverage,
        "fallback": fallback,
        "issues": issues,
    }
