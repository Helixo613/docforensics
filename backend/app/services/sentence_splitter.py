from __future__ import annotations

import re

from app.storage import Sentence
from app.utils.model_loader import get_models

WHITESPACE_RE = re.compile(r"\s+")


def split_pages_into_sentences(
    pages: list[dict[str, int | str]],
    doc_index: int,
    doc_name: str,
) -> list[Sentence]:
    nlp, _, _, _ = get_models()
    sentences: list[Sentence] = []

    for page_entry in pages:
        page_number = int(page_entry["page"])
        text = str(page_entry["text"])
        if not text.strip():
            continue

        doc = nlp(text)
        for span in doc.sents:
            normalized = WHITESPACE_RE.sub(" ", span.text).strip()
            if not normalized:
                continue
            sentences.append(
                Sentence(
                    text=normalized,
                    doc_index=doc_index,
                    doc_name=doc_name,
                    page=page_number,
                    global_index=-1,
                )
            )

    return sentences

