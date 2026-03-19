from __future__ import annotations

import fitz


def extract_pdf_pages(file_bytes: bytes) -> list[dict[str, int | str]]:
    try:
        document = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise ValueError("Invalid PDF file") from exc

    pages: list[dict[str, int | str]] = []
    for page_number, page in enumerate(document, start=1):
        pages.append(
            {
                "page": page_number,
                "text": page.get_text("text"),
            }
        )

    document.close()

    if not any(str(page["text"]).strip() for page in pages):
        raise ValueError("Failed to extract text from PDF")

    return pages

