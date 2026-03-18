from __future__ import annotations

from app.config import MAX_UNCORROBORATED
from app.storage import Sentence, Session


def _claim_payload(sentence: Sentence) -> dict[str, str | int]:
    return {
        "text": sentence.text,
        "doc_name": sentence.doc_name,
        "page": sentence.page,
    }


def _pair_payload(
    item_id: str,
    sentence_a: Sentence,
    sentence_b: Sentence,
    confidence: float,
) -> dict:
    return {
        "id": item_id,
        "claim_a": _claim_payload(sentence_a),
        "claim_b": _claim_payload(sentence_b),
        "confidence": round(confidence, 2),
    }


def build_result_payload(
    session: Session,
    candidate_pairs: list[tuple[int, int, float]],
    classified_pairs: list[tuple[int, int, float, str, float]],
) -> dict:
    contradictions_raw = [
        item for item in classified_pairs if item[3] == "contradiction"
    ]
    agreements_raw = [item for item in classified_pairs if item[3] == "entailment"]

    contradictions_raw.sort(key=lambda item: item[4], reverse=True)
    agreements_raw.sort(key=lambda item: item[4], reverse=True)

    contradictions = [
        _pair_payload(
            f"c_{index}",
            session.sentences[left],
            session.sentences[right],
            confidence,
        )
        for index, (left, right, _, _, confidence) in enumerate(contradictions_raw)
    ]

    agreements = [
        _pair_payload(
            f"a_{index}",
            session.sentences[left],
            session.sentences[right],
            confidence,
        )
        for index, (left, right, _, _, confidence) in enumerate(agreements_raw)
    ]

    matched_indices = {
        index
        for left, right, _ in candidate_pairs
        for index in (left, right)
    }
    uncorroborated_sentences = [
        sentence
        for sentence in session.sentences
        if sentence.global_index not in matched_indices
    ][:MAX_UNCORROBORATED]

    uncorroborated = [
        {
            "id": f"u_{index}",
            "claim": _claim_payload(sentence),
        }
        for index, sentence in enumerate(uncorroborated_sentences)
    ]

    return {
        "session_id": session.session_id,
        "stats": {
            "total_sentences": len(session.sentences),
            "candidate_pairs": len(candidate_pairs),
            "agreements_found": len(agreements),
            "contradictions_found": len(contradictions),
            "uncorroborated_count": len(uncorroborated),
        },
        "contradictions": contradictions,
        "agreements": agreements,
        "uncorroborated": uncorroborated,
    }

