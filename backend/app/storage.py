from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class Sentence:
    text: str
    doc_index: int
    doc_name: str
    page: int
    global_index: int


@dataclass
class Session:
    session_id: str
    documents: list[dict]
    sentences: list[Sentence]
    embeddings: Optional[np.ndarray] = None
    results: Optional[dict] = None
    v2_results: Optional[dict] = None
    v2_source_signature: Optional[str] = None


sessions: dict[str, Session] = {}

