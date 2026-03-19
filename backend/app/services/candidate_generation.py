from __future__ import annotations

import numpy as np

from app.storage import Sentence


def generate_candidate_pairs(
    embeddings: np.ndarray,
    sentences: list[Sentence],
    top_k: int,
    similarity_threshold: float,
) -> list[tuple[int, int, float]]:
    sentence_count = len(sentences)
    if sentence_count < 2 or embeddings.size == 0:
        return []

    similarity_matrix = embeddings @ embeddings.T
    doc_ids = np.array([sentence.doc_index for sentence in sentences], dtype=np.int32)
    same_doc_mask = doc_ids[:, None] == doc_ids[None, :]
    similarity_matrix[same_doc_mask] = -2.0
    np.fill_diagonal(similarity_matrix, -2.0)

    neighbors = min(top_k, sentence_count - 1)
    if neighbors <= 0:
        return []

    deduped_pairs: dict[tuple[int, int], float] = {}
    for idx in range(sentence_count):
        top_indices = np.argpartition(similarity_matrix[idx], -neighbors)[-neighbors:]
        for neighbor_idx in top_indices:
            similarity = float(similarity_matrix[idx][neighbor_idx])
            if similarity < similarity_threshold:
                continue

            left, right = sorted((idx, int(neighbor_idx)))
            if left == right:
                continue

            existing = deduped_pairs.get((left, right))
            if existing is None or similarity > existing:
                deduped_pairs[(left, right)] = similarity

    return [
        (left, right, similarity)
        for (left, right), similarity in sorted(
            deduped_pairs.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]

