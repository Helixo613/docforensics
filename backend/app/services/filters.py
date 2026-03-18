from __future__ import annotations

from app.config import MAX_SENTENCE_CHARS, MIN_WORDS, NOISE_PATTERNS
from app.storage import Sentence


def filter_sentences(sentences: list[Sentence]) -> list[Sentence]:
    filtered: list[Sentence] = []
    seen_texts: set[str] = set()

    for sentence in sentences:
        text = sentence.text.strip()
        if len(text.split()) < MIN_WORDS:
            continue
        if len(text) > MAX_SENTENCE_CHARS:
            continue
        if any(pattern.search(text) for pattern in NOISE_PATTERNS):
            continue
        if text in seen_texts:
            continue
        seen_texts.add(text)
        sentence.text = text
        filtered.append(sentence)

    return filtered


def assign_global_indices(sentences: list[Sentence]) -> None:
    for index, sentence in enumerate(sentences):
        sentence.global_index = index

