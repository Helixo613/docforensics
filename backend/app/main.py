from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.analyze import router as analyze_router
from app.routers.demo import router as demo_router
from app.routers.health import router as health_router
from app.routers.results import router as results_router
from app.routers.search import router as search_router
from app.routers.upload import router as upload_router
from app.utils.model_loader import start_model_loading

app = FastAPI(title="DocForensics AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(results_router)
app.include_router(search_router)
app.include_router(demo_router)


@app.on_event("startup")
def startup_event() -> None:
    start_model_loading()
