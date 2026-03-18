from __future__ import annotations

import numpy as np

from app.storage import Sentence
from app.utils.model_loader import get_models


def classify_candidate_pairs(
    candidate_pairs: list[tuple[int, int, float]],
    sentences: list[Sentence],
    confidence_threshold: float,
) -> list[tuple[int, int, float, str, float]]:
    if not candidate_pairs:
        return []

    _, _, nli_model, labels = get_models()
    text_pairs = [
        (sentences[left].text, sentences[right].text)
        for left, right, _ in candidate_pairs
    ]
    scores = np.asarray(
        nli_model.predict(
            text_pairs,
            batch_size=32,
            apply_softmax=True,
        ),
        dtype=np.float32,
    )

    classified: list[tuple[int, int, float, str, float]] = []
    for (left, right, similarity), score_row in zip(candidate_pairs, scores):
        best_index = int(np.argmax(score_row))
        label = labels[best_index]
        confidence = float(score_row[best_index])
        if confidence < confidence_threshold or label == "neutral":
            continue
        classified.append((left, right, similarity, label, confidence))

    return classified

