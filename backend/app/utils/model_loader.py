from __future__ import annotations

import threading
from typing import Any

import spacy
from sentence_transformers import CrossEncoder, SentenceTransformer

from app.config import EMBEDDING_MODEL, NLI_LABELS, NLI_MODEL, SPACY_MODEL

nlp = None
embedder = None
nli_model = None
nli_labels: list[str] = []
models_loaded = False
models_loading = False
loading_error: str | None = None
_load_lock = threading.Lock()


def _normalize_label(label: str) -> str:
    return label.strip().lower().replace("_", " ")


def _resolve_nli_labels(model: CrossEncoder) -> list[str]:
    config: Any = getattr(model, "model", None)
    config = getattr(config, "config", None)
    id2label = getattr(config, "id2label", None)
    if not id2label:
        raise RuntimeError("NLI model config missing id2label mapping")

    ordered_keys = sorted(id2label.keys(), key=int)
    labels = [_normalize_label(str(id2label[key])) for key in ordered_keys]
    expected = {"contradiction", "entailment", "neutral"}
    if set(labels) != expected:
        raise RuntimeError(
            f"Unexpected NLI labels from model config: {labels}. "
            f"Expected a permutation of {NLI_LABELS}."
        )
    return labels


def load_models() -> None:
    global nlp, embedder, nli_model, nli_labels
    global models_loaded, models_loading, loading_error

    with _load_lock:
        if models_loaded:
            return

        models_loading = True
        loading_error = None

        try:
            print("Loading spaCy model...")
            nlp = spacy.load(
                SPACY_MODEL,
                disable=["ner", "lemmatizer", "attribute_ruler"],
            )

            print("Loading embedding model...")
            embedder = SentenceTransformer(EMBEDDING_MODEL)

            print("Loading NLI model...")
            nli_model = CrossEncoder(NLI_MODEL)
            nli_labels = _resolve_nli_labels(nli_model)

            print("Running warmup...")
            embedder.encode(["warmup"], normalize_embeddings=True)
            nli_model.predict([("warmup a", "warmup b")], apply_softmax=True)

            models_loaded = True
            print("Models loaded and warmed up.")
        except Exception as exc:
            models_loaded = False
            loading_error = str(exc)
            print(f"Model load failed: {exc}")
        finally:
            models_loading = False


def start_model_loading() -> None:
    if models_loaded or models_loading:
        return

    thread = threading.Thread(target=load_models, daemon=True)
    thread.start()


def get_models() -> tuple[Any, Any, Any, list[str]]:
    if not models_loaded or nlp is None or embedder is None or nli_model is None:
        raise RuntimeError(loading_error or "Models are not loaded")
    return nlp, embedder, nli_model, nli_labels


def get_health_payload() -> dict[str, bool | str]:
    if models_loaded:
        return {
            "status": "ok",
            "models_loaded": True,
        }
    if models_loading:
        return {
            "status": "loading",
            "models_loaded": False,
        }
    if loading_error:
        return {
            "status": "error",
            "models_loaded": False,
            "error": loading_error,
        }
    return {
        "status": "loading",
        "models_loaded": False,
    }


def are_models_loaded() -> bool:
    return models_loaded
