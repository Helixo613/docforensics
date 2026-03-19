from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from app.routers.v2 import analyze_session_v2, get_v2_results
from app.schemas import AnalyzeOverrides
from app.services.pair_analysis import build_or_get_pair_analysis
from app.services.v2_issue_map import build_issue_map, build_pair_relation_signature
from app.storage import Session, sessions


BACKEND_ROOT = Path(__file__).resolve().parents[1]


class V2IssueMapServiceTests(unittest.TestCase):
    def load_demo_payload(self, filename: str) -> dict:
        with (BACKEND_ROOT / filename).open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def test_build_issue_map_from_primary_demo(self) -> None:
        payload = self.load_demo_payload("demo_session.json")

        issue_map = build_issue_map(payload)

        self.assertEqual(issue_map["stats"]["total_issues"], 1)
        self.assertEqual(issue_map["stats"]["total_claims"], 4)
        self.assertEqual(issue_map["stats"]["contested_issues"], 1)
        self.assertEqual(issue_map["stats"]["unclear_issues"], 0)
        self.assertFalse(issue_map["fallback"]["should_fallback"])
        self.assertEqual(issue_map["coverage"]["pair_derived_claims_total"], 4)
        self.assertEqual(issue_map["coverage"]["pair_derived_claims_represented_in_issues"], 4)
        self.assertEqual(issue_map["coverage"]["pair_relations_total"], 4)
        self.assertEqual(issue_map["coverage"]["pair_relations_represented_in_issues"], 4)
        self.assertEqual(issue_map["coverage"]["structurally_ambiguous_claims_in_issues"], 0)
        self.assertEqual(issue_map["coverage"]["uncorroborated_claims_outside_issue_map"], 1)

        contested_issue = issue_map["issues"][0]
        self.assertEqual(contested_issue["status"], "contested")
        self.assertEqual(contested_issue["structural_quality"], "clean")
        self.assertFalse(contested_issue["merge_risk"])
        self.assertEqual(contested_issue["label_kind"], "representative_claim_excerpt")
        self.assertTrue(contested_issue["label_claim_id"].startswith("cl_"))
        self.assertEqual(len(contested_issue["sides"]), 2)

        document_positions = {
            item["doc_name"]: item["position"]
            for item in contested_issue["document_positions"]
        }
        self.assertEqual(document_positions["finetuning_excerpt.pdf"], "side_1")
        self.assertEqual(document_positions["chextransfer_excerpt.pdf"], "side_0")
        self.assertEqual(document_positions["supervised_transfer_scale_excerpt.pdf"], "side_0")

    def test_build_issue_map_ignores_uncorroborated_claims(self) -> None:
        payload = {
            "session_id": "uncorroborated-only",
            "stats": {
                "total_sentences": 4,
                "candidate_pairs": 0,
                "agreements_found": 0,
                "contradictions_found": 0,
                "uncorroborated_count": 4,
            },
            "contradictions": [],
            "agreements": [],
            "uncorroborated": [
                {
                    "id": f"u_{index}",
                    "claim": {
                        "text": f"Standalone claim {index}",
                        "doc_name": f"doc_{index}.pdf",
                        "page": 1,
                    },
                }
                for index in range(4)
            ],
        }

        issue_map = build_issue_map(payload)

        self.assertTrue(issue_map["fallback"]["should_fallback"])
        self.assertIn("no_issue_structure", issue_map["fallback"]["reasons"])
        self.assertEqual(issue_map["stats"]["total_issues"], 0)
        self.assertEqual(issue_map["stats"]["total_claims"], 0)
        self.assertEqual(issue_map["coverage"]["pair_derived_claims_total"], 0)
        self.assertEqual(issue_map["coverage"]["pair_relations_total"], 0)
        self.assertEqual(issue_map["coverage"]["uncorroborated_claims_outside_issue_map"], 4)

    def test_pair_signature_is_order_insensitive_for_equivalent_pair_evidence(self) -> None:
        payload = {
            "session_id": "same-session",
            "agreements": [
                {
                    "id": "a_0",
                    "claim_a": {"text": "Claim one", "doc_name": "doc_a.pdf", "page": 1},
                    "claim_b": {"text": "Claim two", "doc_name": "doc_b.pdf", "page": 2},
                    "confidence": 0.91,
                },
                {
                    "id": "a_1",
                    "claim_a": {"text": "Claim three", "doc_name": "doc_c.pdf", "page": 3},
                    "claim_b": {"text": "Claim four", "doc_name": "doc_d.pdf", "page": 4},
                    "confidence": 0.87,
                },
            ],
            "contradictions": [
                {
                    "id": "c_0",
                    "claim_a": {"text": "Claim five", "doc_name": "doc_e.pdf", "page": 5},
                    "claim_b": {"text": "Claim six", "doc_name": "doc_f.pdf", "page": 6},
                    "confidence": 0.93,
                }
            ],
            "uncorroborated": [
                {
                    "id": "u_0",
                    "claim": {"text": "Ignored", "doc_name": "doc_g.pdf", "page": 7},
                }
            ],
        }
        reordered_payload = {
            "session_id": "same-session",
            "agreements": [
                {
                    "id": "a_9",
                    "claim_a": {"text": "Claim four", "doc_name": "doc_d.pdf", "page": 4},
                    "claim_b": {"text": "Claim three", "doc_name": "doc_c.pdf", "page": 3},
                    "confidence": 0.87,
                },
                {
                    "id": "a_8",
                    "claim_a": {"text": "Claim two", "doc_name": "doc_b.pdf", "page": 2},
                    "claim_b": {"text": "Claim one", "doc_name": "doc_a.pdf", "page": 1},
                    "confidence": 0.91,
                },
            ],
            "contradictions": [
                {
                    "id": "c_9",
                    "claim_a": {"text": "Claim six", "doc_name": "doc_f.pdf", "page": 6},
                    "claim_b": {"text": "Claim five", "doc_name": "doc_e.pdf", "page": 5},
                    "confidence": 0.93,
                }
            ],
            "uncorroborated": [],
        }

        self.assertEqual(
            build_pair_relation_signature(payload),
            build_pair_relation_signature(reordered_payload),
        )

    def test_pair_signature_depends_on_evidence_not_session_identity(self) -> None:
        payload = {
            "session_id": "session-a",
            "agreements": [
                {
                    "id": "a_0",
                    "claim_a": {"text": "Claim one", "doc_name": "doc_a.pdf", "page": 1},
                    "claim_b": {"text": "Claim two", "doc_name": "doc_b.pdf", "page": 2},
                    "confidence": 0.91,
                }
            ],
            "contradictions": [
                {
                    "id": "c_0",
                    "claim_a": {"text": "Claim three", "doc_name": "doc_c.pdf", "page": 3},
                    "claim_b": {"text": "Claim four", "doc_name": "doc_d.pdf", "page": 4},
                    "confidence": 0.88,
                }
            ],
            "uncorroborated": [],
        }
        same_evidence_different_session = {
            **payload,
            "session_id": "session-b",
        }

        self.assertEqual(
            build_pair_relation_signature(payload),
            build_pair_relation_signature(same_evidence_different_session),
        )

    def test_issue_quality_and_merge_risk_flag_broad_sparse_component(self) -> None:
        payload = {
            "session_id": "broad-component",
            "stats": {
                "total_sentences": 5,
                "candidate_pairs": 4,
                "agreements_found": 2,
                "contradictions_found": 2,
                "uncorroborated_count": 0,
            },
            "agreements": [
                {
                    "id": "a_0",
                    "claim_a": {"text": "Claim A", "doc_name": "doc_a.pdf", "page": 1},
                    "claim_b": {"text": "Claim B", "doc_name": "doc_b.pdf", "page": 1},
                    "confidence": 0.91,
                },
                {
                    "id": "a_1",
                    "claim_a": {"text": "Claim C", "doc_name": "doc_c.pdf", "page": 1},
                    "claim_b": {"text": "Claim D", "doc_name": "doc_d.pdf", "page": 1},
                    "confidence": 0.9,
                },
            ],
            "contradictions": [
                {
                    "id": "c_0",
                    "claim_a": {"text": "Claim B", "doc_name": "doc_b.pdf", "page": 1},
                    "claim_b": {"text": "Claim C", "doc_name": "doc_c.pdf", "page": 1},
                    "confidence": 0.92,
                },
                {
                    "id": "c_1",
                    "claim_a": {"text": "Claim D", "doc_name": "doc_d.pdf", "page": 1},
                    "claim_b": {"text": "Claim E", "doc_name": "doc_e.pdf", "page": 1},
                    "confidence": 0.89,
                },
            ],
            "uncorroborated": [],
        }

        issue_map = build_issue_map(payload)

        self.assertEqual(issue_map["stats"]["total_issues"], 1)
        self.assertEqual(issue_map["coverage"]["pair_derived_claims_total"], 5)
        self.assertEqual(issue_map["coverage"]["pair_relations_total"], 4)
        issue = issue_map["issues"][0]
        self.assertTrue(issue["merge_risk"])
        self.assertEqual(issue["structural_quality"], "borderline")
        self.assertEqual(issue["label_kind"], "representative_claim_excerpt")
        self.assertTrue(issue["label_claim_id"].startswith("cl_"))


class V2IssueMapApiTests(unittest.TestCase):
    def setUp(self) -> None:
        sessions.clear()

    def tearDown(self) -> None:
        sessions.clear()

    def test_v2_route_functions_use_cached_pair_results(self) -> None:
        with (BACKEND_ROOT / "demo_session_2.json").open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        sessions["seeded"] = Session(
            session_id="seeded",
            documents=[],
            sentences=[],
            results={**payload, "session_id": "seeded"},
        )

        analyze_body = analyze_session_v2("seeded", None)
        self.assertEqual(analyze_body["session_id"], "seeded")
        self.assertEqual(analyze_body["source"], "v1_pair_results")
        self.assertGreaterEqual(analyze_body["stats"]["mixed_issues"], 1)

        get_body = get_v2_results("seeded")
        self.assertEqual(get_body, analyze_body)

    def test_v2_cache_is_invalidated_when_pair_results_change(self) -> None:
        with (BACKEND_ROOT / "demo_session.json").open("r", encoding="utf-8") as handle:
            payload_a = json.load(handle)
        with (BACKEND_ROOT / "demo_session_2.json").open("r", encoding="utf-8") as handle:
            payload_b = json.load(handle)

        sessions["seeded"] = Session(
            session_id="seeded",
            documents=[],
            sentences=[],
            results={**payload_a, "session_id": "seeded"},
        )

        original_signature = build_pair_relation_signature(sessions["seeded"].results)
        first_issue_map = analyze_session_v2("seeded", None)
        self.assertEqual(first_issue_map["stats"]["total_issues"], 1)
        self.assertEqual(first_issue_map["issues"][0]["status"], "contested")

        sessions["seeded"].results = {**payload_b, "session_id": "seeded"}
        updated_signature = build_pair_relation_signature(sessions["seeded"].results)
        self.assertNotEqual(original_signature, updated_signature)

        stale_response = get_v2_results("seeded")
        self.assertEqual(stale_response.status_code, 404)
        self.assertEqual(stale_response.body.decode("utf-8"), '{"error":"V2 analysis not yet run"}')
        self.assertIsNone(sessions["seeded"].v2_results)
        self.assertIsNone(sessions["seeded"].v2_source_signature)

        refreshed_issue_map = analyze_session_v2("seeded", None)
        self.assertEqual(refreshed_issue_map["stats"]["total_issues"], 1)
        self.assertEqual(refreshed_issue_map["issues"][0]["status"], "mixed")
        self.assertNotEqual(refreshed_issue_map, first_issue_map)


class PairAnalysisInvalidationTests(unittest.TestCase):
    def setUp(self) -> None:
        sessions.clear()

    def tearDown(self) -> None:
        sessions.clear()

    def test_pair_reanalysis_clears_v2_cache(self) -> None:
        session = Session(
            session_id="seeded",
            documents=[],
            sentences=[],
            results={"session_id": "old"},
            v2_results={"session_id": "old", "issues": []},
            v2_source_signature="old-signature",
        )

        with patch("app.services.pair_analysis.build_embeddings", return_value=[]), patch(
            "app.services.pair_analysis.generate_candidate_pairs",
            return_value=[],
        ), patch(
            "app.services.pair_analysis.classify_candidate_pairs",
            return_value=[],
        ), patch(
            "app.services.pair_analysis.build_result_payload",
            return_value={
                "session_id": "seeded",
                "stats": {
                    "total_sentences": 0,
                    "candidate_pairs": 0,
                    "agreements_found": 0,
                    "contradictions_found": 0,
                    "uncorroborated_count": 0,
                },
                "contradictions": [],
                "agreements": [],
                "uncorroborated": [],
            },
        ):
            result = build_or_get_pair_analysis(
                session,
                overrides=AnalyzeOverrides(top_k=1),
            )

        self.assertEqual(result["session_id"], "seeded")
        self.assertIsNone(session.v2_results)
        self.assertIsNone(session.v2_source_signature)


if __name__ == "__main__":
    unittest.main()
