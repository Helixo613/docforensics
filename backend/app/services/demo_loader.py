from __future__ import annotations

import json
from pathlib import Path

from app.config import DEMO_SESSION_PATH, DEMO_SESSION_SECONDARY_PATH

DEMO_DATASETS = {
    "primary": DEMO_SESSION_PATH,
    "secondary": DEMO_SESSION_SECONDARY_PATH,
}


def load_demo_payload(dataset: str = "primary") -> dict:
    backend_root = Path(__file__).resolve().parents[2]
    demo_name = DEMO_DATASETS.get(dataset)
    if demo_name is None:
        raise ValueError("Unknown demo dataset")

    demo_path = backend_root / demo_name
    if not demo_path.exists():
        raise FileNotFoundError("Demo data not found")

    with demo_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
