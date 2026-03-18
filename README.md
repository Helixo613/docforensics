# DocForensics AI

Cross-document contradiction and agreement detection for PDF collections.

Upload 2-10 research papers or reports and the system finds where they agree, where they contradict each other, and which claims have no corroboration from the other uploaded documents. Every result links back to the source document, page number, and exact text.

Built for Hackstreet 4.0 / Pentathon 3.0 (March 2026), addressing Problem Statement 3: AI Knowledge Discovery Engine for Unstructured Data.

## Project Structure

```
backend/     FastAPI + NLP pipeline (Python)
frontend/    Flutter app (coming soon)
```

## Backend

The backend runs a six-stage NLP pipeline: PDF extraction, sentence splitting, embedding, cross-document candidate generation, NLI classification, and result bucketing. See [`backend/README.md`](backend/README.md) for full setup instructions, API spec, and architecture details.

**Quick start (WSL):**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Tech Stack

- **Backend:** Python, FastAPI, PyMuPDF, spaCy, sentence-transformers, DeBERTa NLI cross-encoder
- **Frontend:** Flutter (in progress)
- **Storage:** In-memory (hackathon MVP, no database)
- **Models:** All pre-trained, CPU inference, no GPU required
