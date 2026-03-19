from __future__ import annotations

from fastapi import APIRouter

from app.schemas import HealthResponse
from app.utils.model_loader import get_health_payload

router = APIRouter()


@router.get("/health", response_model=HealthResponse, response_model_exclude_none=True)
def health_check() -> dict:
    return get_health_payload()
