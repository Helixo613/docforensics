from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.schemas import AnalysisResult, ErrorResponse
from app.services.demo_loader import load_demo_payload

router = APIRouter()


@router.get(
    "/demo",
    response_model=AnalysisResult,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def get_demo(dataset: str = Query(default="primary")):
    try:
        return load_demo_payload(dataset=dataset)
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Unknown demo dataset"})
    except FileNotFoundError:
        return JSONResponse(status_code=500, content={"error": "Demo data not found"})
