from __future__ import annotations

import numpy as np

from app.storage import Sentence
from app.utils.model_loader import get_models


def build_embeddings(sentences: list[Sentence]) -> np.ndarray:
    if not sentences:
        return np.empty((0, 0), dtype=np.float32)

    _, embedder, _, _ = get_models()
    texts = [sentence.text for sentence in sentences]
    vectors = embedder.encode(
        texts,
        batch_size=64,
        normalize_embeddings=True,
    )
    return np.asarray(vectors, dtype=np.float32)

