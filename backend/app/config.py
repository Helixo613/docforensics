from __future__ import annotations

import re

# --- Sentence filtering ---
MIN_WORDS = 16
MAX_SENTENCE_CHARS = 500

# --- Candidate generation ---
TOP_K = 3
SIMILARITY_THRESHOLD = 0.5

# --- NLI classification ---
CONFIDENCE_THRESHOLD = 0.75

# --- Output limits ---
MAX_UNCORROBORATED = 30

# --- Upload limits ---
MAX_FILES = 10
MIN_FILES = 2
MAX_FILE_SIZE_MB = 20

# --- Models ---
SPACY_MODEL = "en_core_web_sm"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
NLI_MODEL = "cross-encoder/nli-deberta-v3-xsmall"

# --- NLI label mapping (fallback only; runtime verification still happens) ---
NLI_LABELS = ["contradiction", "entailment", "neutral"]

# --- Demo ---
DEMO_SESSION_PATH = "demo_session.json"
DEMO_SESSION_SECONDARY_PATH = "demo_session_2.json"

# --- Filtering ---
NOISE_PATTERNS = [
    re.compile(r"^\[?\d+[\].\)]\s"),
    re.compile(r"^(figure|table|fig\.|tab\.)\s", re.IGNORECASE),
    re.compile(r"https?://"),
    re.compile(r"^[A-Z\s\d]{15,}$"),
    re.compile(r"^\d+$"),
]
