from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.config import MAX_FILE_SIZE_MB, MAX_FILES, MIN_FILES
from app.schemas import ErrorResponse, UploadResponse
from app.services.filters import assign_global_indices, filter_sentences
from app.services.pdf_extractor import extract_pdf_pages
from app.services.sentence_splitter import split_pages_into_sentences
from app.storage import Session, sessions
from app.utils.model_loader import are_models_loaded

router = APIRouter()


def _get_upload_size(upload: UploadFile) -> int:
    size = getattr(upload, "size", None)
    if size is not None:
        return int(size)

    file_obj = upload.file
    current_position = file_obj.tell()
    file_obj.seek(0, 2)
    size = file_obj.tell()
    file_obj.seek(current_position)
    return int(size)


@router.post(
    "/upload",
    response_model=UploadResponse,
    responses={
        400: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
async def upload_documents(files: list[UploadFile] = File(...)):
    if not are_models_loaded():
        return JSONResponse(status_code=503, content={"error": "Models not loaded"})

    if len(files) < MIN_FILES or len(files) > MAX_FILES:
        return JSONResponse(
            status_code=400,
            content={"error": f"Upload between {MIN_FILES} and {MAX_FILES} PDF files"},
        )

    documents: list[dict] = []
    all_sentences = []

    for doc_index, upload in enumerate(files):
        filename = upload.filename or f"document_{doc_index + 1}.pdf"
        file_size = _get_upload_size(upload)
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return JSONResponse(
                status_code=400,
                content={"error": f"File {filename} exceeds {MAX_FILE_SIZE_MB}MB limit"},
            )
        await upload.seek(0)
        file_bytes = await upload.read()

        try:
            pages = extract_pdf_pages(file_bytes)
        except ValueError:
            return JSONResponse(
                status_code=422,
                content={"error": f"Failed to extract text from {filename}"},
            )

        sentences = split_pages_into_sentences(pages, doc_index=doc_index, doc_name=filename)
        filtered_sentences = filter_sentences(sentences)

        documents.append(
            {
                "name": filename,
                "pages": len(pages),
                "sentences": len(filtered_sentences),
            }
        )
        all_sentences.extend(filtered_sentences)

    assign_global_indices(all_sentences)

    session_id = uuid4().hex[:8]
    sessions[session_id] = Session(
        session_id=session_id,
        documents=documents,
        sentences=all_sentences,
    )

    return {
        "session_id": session_id,
        "documents": documents,
        "total_sentences": len(all_sentences),
    }
