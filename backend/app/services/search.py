from __future__ import annotations

import numpy as np

from app.storage import Session
from app.utils.model_loader import get_models

SEARCH_RESULT_LIMIT = 5


def search_session_sentences(session: Session, query: str) -> dict:
    if session.embeddings is None:
        raise ValueError("Embeddings unavailable; run analysis first")
    if not session.sentences or session.embeddings.size == 0:
        return {
            "session_id": session.session_id,
            "query": query,
            "results": [],
        }

    _, embedder, _, _ = get_models()
    query_embedding = np.asarray(
        embedder.encode([query], normalize_embeddings=True),
        dtype=np.float32,
    )[0]
    scores = session.embeddings @ query_embedding
    top_indices = np.argsort(scores)[-SEARCH_RESULT_LIMIT:][::-1]

    return {
        "session_id": session.session_id,
        "query": query,
        "results": [
            {
                "text": session.sentences[index].text,
                "doc_name": session.sentences[index].doc_name,
                "page": session.sentences[index].page,
                "score": round(float(scores[index]), 2),
            }
            for index in top_indices
        ],
    }
