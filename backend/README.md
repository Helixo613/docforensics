# DocForensics AI Backend

Cross-document contradiction and agreement detection for PDF collections. Upload research papers, reports, or any digital-native PDFs and the system finds where they agree, where they contradict each other, and which claims have no corroboration from the other uploaded documents. Every result is traceable to a specific document, page, and text snippet.

Built for Hackstreet 4.0 (March 2026) as a hackathon MVP backend.

## What This Backend Does

Given 2-10 uploaded PDFs, the backend runs a six-stage NLP pipeline:

1. **Extract** page-level text from each PDF using PyMuPDF
2. **Split** text into sentences using spaCy and filter out noise (short fragments, references, headers, URLs)
3. **Embed** all surviving sentences using a lightweight sentence transformer
4. **Generate candidates** by finding the top-K most similar sentences across different documents
5. **Classify** each candidate pair as agreement, contradiction, or neutral using an NLI cross-encoder
6. **Bucket** results into three categories and return a structured Consensus Brief

The output is a JSON response with contradictions, agreements, and uncorroborated claims, each with source document name, page number, and the exact text snippet.

## Architecture Overview

```
               POST /upload              POST /analyze/{sid}
Flutter App  ──────────────►  FastAPI  ──────────────────────►  NLP Pipeline
                                 │                                   │
                                 │  in-memory sessions dict          │
                                 │  (no database)                    │
                                 │                                   ▼
                              GET /results/{sid}              ┌─────────────┐
                              GET /search/{sid}?q=...         │ PyMuPDF     │
                              GET /demo                       │ spaCy       │
                              GET /health                     │ MiniLM-L6   │
                                                              │ DeBERTa NLI │
                                                              └─────────────┘
```

Single FastAPI process. No database. No message queue. No microservices. Session state lives in a Python dict and is lost on restart.

Three pre-trained models are loaded at startup in a daemon thread (see `utils/model_loader.py`). The server accepts HTTP requests immediately, but `/upload` and `/analyze` return `503` until loading finishes:

| Model | Purpose | Size |
|---|---|---|
| `en_core_web_sm` (spaCy) | Sentence splitting | ~12 MB |
| `all-MiniLM-L6-v2` (sentence-transformers) | Sentence embeddings (384-dim, L2-normalized) | ~80 MB |
| `cross-encoder/nli-deberta-v3-xsmall` | Contradiction/entailment classification | ~90 MB |

## Project Structure

```
backend/
  app/
    main.py                  # FastAPI app, CORS, router registration, startup hook
    config.py                # All tunable thresholds and model identifiers
    storage.py               # Session/Sentence dataclasses, in-memory sessions dict
    schemas.py               # Pydantic request/response models
    routers/
      health.py              # GET /health
      upload.py              # POST /upload
      analyze.py             # POST /analyze/{session_id}
      results.py             # GET /results/{session_id}
      search.py              # GET /search/{session_id}
      demo.py                # GET /demo
    services/
      pdf_extractor.py       # PyMuPDF text extraction per page
      sentence_splitter.py   # spaCy sentence splitting
      filters.py             # Noise regex filters, min-word filter, dedup
      embeddings.py          # Sentence embedding via MiniLM
      candidate_generation.py # Cross-doc top-K nearest neighbor pairs
      nli.py                 # NLI classification via DeBERTa cross-encoder
      bucketing.py           # Result bucketing and response formatting
      search.py              # Semantic search over session embeddings
      demo_loader.py         # Load pre-baked demo JSON from disk
    utils/
      model_loader.py        # Background model loading, warmup, health state
  demo_papers/               # Primary demo dataset (3 curated excerpt PDFs)
  demo_papers_secondary/     # Secondary demo dataset (3 curated excerpt PDFs)
  demo_session.json          # Frozen primary demo results
  demo_session_2.json        # Frozen secondary demo results
  requirements.txt
  README.md
```

## Setup and Run (WSL)

Requires Python 3.10+ on WSL.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**First startup notes:**

- `pip install` pulls in PyTorch and the transformer libraries, which can be several GB on a fresh WSL machine. Budget time for this.
- The Hugging Face models (`all-MiniLM-L6-v2` and `cross-encoder/nli-deberta-v3-xsmall`) are downloaded automatically on first run. This requires internet and takes a few minutes.
- Check `GET /health` to monitor loading state.
- Session data is in-memory only. Restarting the server clears all uploads and cached results.

## API Endpoints

All result-returning endpoints (`/analyze`, `/results`, `/demo`) use the same response shape. Internal fields like `global_index`, raw embeddings, similarity scores, and NLI label strings are never exposed.

---

### `GET /health`

Check if the server is up and models are loaded.

**Response:**

```json
// Models ready
{ "status": "ok", "models_loaded": true }

// Still loading
{ "status": "loading", "models_loaded": false }

// Startup failed
{ "status": "error", "models_loaded": false, "error": "..." }
```

---

### `POST /upload`

Upload 2-10 PDF files. Extracts text, splits sentences, filters noise.

**Request:** `multipart/form-data` with field `files` containing PDF uploads.

**Validation:**
- Minimum 2, maximum 10 files
- Each file max 20 MB
- Must be valid PDFs (PyMuPDF can open them)
- Models must be loaded (returns `503` otherwise)

**Response (200):**

```json
{
  "session_id": "a1b2c3d4",
  "documents": [
    { "name": "paper1.pdf", "pages": 12, "sentences": 87 },
    { "name": "paper2.pdf", "pages": 8, "sentences": 54 }
  ],
  "total_sentences": 141
}
```

**Errors:** `400` (file count/size), `422` (extraction failure), `503` (models not loaded).

---

### `POST /analyze/{session_id}`

Run the full NLP pipeline on an uploaded session. Results are cached — calling again with no overrides returns the cached result.

**Request body (optional):** JSON with threshold overrides for tuning.

```json
{
  "similarity_threshold": 0.45,
  "confidence_threshold": 0.7,
  "top_k": 4
}
```

If omitted or all fields null, config.py defaults are used. Providing any override forces a fresh pipeline run.

**Response (200):** Consensus Brief (shared result shape, see below).

**Errors:** `404` (session not found), `503` (models not loaded).

---

### `GET /results/{session_id}`

Return cached analysis results without re-running the pipeline.

**Response (200):** Consensus Brief (shared result shape).

**Errors:** `404` (session not found, or analysis not yet run).

---

### `GET /search/{session_id}?q=...`

Semantic search across all sentences in a session. Requires that `/analyze` has been called first (embeddings must exist).

**Query parameters:** `q` (required, non-empty search query).

**Response (200):**

```json
{
  "session_id": "a1b2c3d4",
  "query": "transfer learning",
  "results": [
    {
      "text": "Transfer learning from ImageNet significantly improved performance.",
      "doc_name": "paper1.pdf",
      "page": 4,
      "score": 0.74
    }
  ]
}
```

Returns the top 5 results ranked by cosine similarity to the query. Scores are rounded to 2 decimal places. No minimum relevance threshold is applied — all 5 are returned regardless of score.

**Errors:** `400` (empty query), `404` (session not found), `409` (embeddings not yet generated), `503` (models not loaded).

---

### `GET /demo?dataset=primary`

Load pre-baked demo results from disk. No pipeline runs. No session needed.

**Query parameters:** `dataset` (optional, default `"primary"`). Accepts `"primary"` or `"secondary"`.

**Response (200):** Consensus Brief (shared result shape).

**Errors:** `400` (unknown dataset name), `500` (demo JSON file not found on disk).

---

### Shared Result Shape

Every endpoint that returns analysis results uses this structure. Trimmed from the actual primary demo payload (`demo_session.json`):

```json
{
  "session_id": "bc95a1e5",
  "stats": {
    "total_sentences": 7,
    "candidate_pairs": 9,
    "agreements_found": 1,
    "contradictions_found": 3,
    "uncorroborated_count": 1
  },
  "contradictions": [
    {
      "id": "c_0",
      "claim_a": {
        "text": "ImageNet pretraining yields a statistically significant boost in performance across architectures, with a higher boost for smaller architectures.",
        "doc_name": "chextransfer_excerpt.pdf",
        "page": 1
      },
      "claim_b": {
        "text": "ImageNet pretraining is less advantageous than previously thought for medical imaging, and its benefit should be evaluated case by case.",
        "doc_name": "finetuning_excerpt.pdf",
        "page": 1
      },
      "confidence": 0.98
    }
  ],
  "agreements": [
    {
      "id": "a_0",
      "claim_a": {
        "text": "Transfer learning using pretrained ImageNet models has been the standard approach for chest X ray tasks and many other medical imaging modalities.",
        "doc_name": "chextransfer_excerpt.pdf",
        "page": 1
      },
      "claim_b": {
        "text": "Transfer learning using pretrained ImageNet models has been a standard approach in many medical imaging tasks.",
        "doc_name": "supervised_transfer_scale_excerpt.pdf",
        "page": 1
      },
      "confidence": 0.99
    }
  ],
  "uncorroborated": [
    {
      "id": "u_0",
      "claim": {
        "text": "The truncated models maintained favorable accuracy to parameter tradeoffs, making compact backbones attractive for resource constrained medical imaging deployments.",
        "doc_name": "chextransfer_excerpt.pdf",
        "page": 1
      }
    }
  ]
}
```

Each claim includes the source document name, page number, and exact text snippet. Contradictions and agreements are sorted by confidence (highest first). Uncorroborated claims are capped at 30.

## Demo Datasets

Two frozen demo datasets ship with the backend for reliable demo fallback.

### Primary (`demo_papers/`)

Three one-page excerpt PDFs on whether ImageNet transfer learning helps medical imaging:

- `chextransfer_excerpt.pdf` — argues pretraining yields a statistically significant boost
- `supervised_transfer_scale_excerpt.pdf` — argues large-scale supervised pretraining transfers well
- `finetuning_excerpt.pdf` — argues pretraining is less advantageous than previously thought

Produces: 3 contradictions, 1 agreement, 1 uncorroborated claim.

### Secondary (`demo_papers_secondary/`)

Three one-page excerpt PDFs on a related but distinct angle — whether medical-domain pretraining outperforms generic ImageNet transfer:

- `transfusion_excerpt.pdf` — argues transfer learning offers limited gains because medical images differ from natural images
- `novel_transfer_learning_excerpt.pdf` — argues medical pretraining significantly improves performance when labeled data is limited
- `self_supervised_transfer_excerpt.pdf` — argues self-supervised medical pretraining improves downstream performance

Produces: 3 contradictions, 2 agreements, 0 uncorroborated claims.

Both datasets use curated excerpt PDFs rather than full papers. This is intentional — the backend does not do section detection or deep metadata cleanup, so full papers can produce noisy results from method sections, boilerplate, and citation fragments. Excerpt PDFs keep the demo stable.

### Regenerating demo JSON

To regenerate `demo_session.json` from the curated PDFs:

```bash
# Upload
curl -X POST http://127.0.0.1:8000/upload \
  -F "files=@demo_papers/chextransfer_excerpt.pdf" \
  -F "files=@demo_papers/supervised_transfer_scale_excerpt.pdf" \
  -F "files=@demo_papers/finetuning_excerpt.pdf"

# Analyze (use session_id from upload response)
curl -X POST http://127.0.0.1:8000/analyze/<session_id>

# Save the response body as demo_session.json
```

## Semantic Search

The `/search` endpoint encodes the query with MiniLM and runs cosine similarity against the sentence embeddings already computed by `/analyze`. It requires that `/analyze` has been called first on the session — otherwise it returns `409`.

Search is a supplementary feature. The Consensus Brief is the primary output.

## Tuned Defaults

All thresholds live in `app/config.py`:

| Parameter | Value | Purpose |
|---|---|---|
| `MIN_WORDS` | 16 | Minimum words per sentence to keep. Raised from 8 after validation — removes metadata fragments and boilerplate. |
| `MAX_SENTENCE_CHARS` | 500 | Drop abnormally long sentences (table dumps, concatenated text). |
| `TOP_K` | 3 | Nearest cross-document neighbors per sentence for candidate generation. |
| `SIMILARITY_THRESHOLD` | 0.5 | Minimum cosine similarity to become a candidate pair. |
| `CONFIDENCE_THRESHOLD` | 0.75 | Minimum NLI confidence to surface a result. |
| `MAX_UNCORROBORATED` | 30 | Cap on uncorroborated claims in the response. |
| `MAX_FILES` | 10 | Maximum PDFs per upload. |
| `MIN_FILES` | 2 | Minimum PDFs per upload. |
| `MAX_FILE_SIZE_MB` | 20 | Per-file size limit. |

These were tuned for demo quality on the curated datasets, not for broad recall on arbitrary full papers.

## NLI Label Handling

The backend does not hardcode the NLI label order. At startup, it reads `id2label` from the loaded Hugging Face model config and verifies the labels are a permutation of `{contradiction, entailment, neutral}`. If the check fails, `/health` reports an error and the pipeline refuses to run.

This prevents silent inversion of contradiction vs. entailment if the model or its config changes.

## Current Limitations

- **In-memory only.** No database, no persistence. Server restart clears everything. This is fine for a single-user demo.
- **Not production-grade.** No auth, no rate limiting, no concurrent session isolation, no deployment infrastructure.
- **Digital-native PDFs only.** Scanned PDFs or image-based PDFs will extract poorly or produce empty text. The pipeline has no OCR.
- **Full papers are noisy.** Method sections, publication metadata, and citation boilerplate can produce false positive contradictions. The curated demo excerpts avoid this by design.
- **Dense similarity matrix.** The candidate generation step computes an NxN similarity matrix in memory. For the expected scale (10 docs, ~500 sentences), this is ~1 MB and fast. It would not scale to thousands of documents without a different approach.
- **No duplicate upload check.** The same PDF can be uploaded twice in one session. The backend treats them as separate documents.
- **Upload size validation is practical, not strict.** FastAPI/Starlette parses the full multipart body before the endpoint code runs. The size check prevents extra application-level memory use but does not enforce a true streaming hard limit.

## Manual Testing

```bash
# Health check
curl http://127.0.0.1:8000/health

# Upload 2 PDFs
curl -X POST http://127.0.0.1:8000/upload \
  -F "files=@/path/to/paper1.pdf" \
  -F "files=@/path/to/paper2.pdf"

# Run analysis
curl -X POST http://127.0.0.1:8000/analyze/<session_id>

# Run analysis with overrides
curl -X POST http://127.0.0.1:8000/analyze/<session_id> \
  -H "Content-Type: application/json" \
  -d '{"similarity_threshold": 0.45, "confidence_threshold": 0.7, "top_k": 4}'

# Fetch cached results
curl http://127.0.0.1:8000/results/<session_id>

# Semantic search
curl "http://127.0.0.1:8000/search/<session_id>?q=transfer%20learning"

# Load primary demo
curl http://127.0.0.1:8000/demo

# Load secondary demo
curl "http://127.0.0.1:8000/demo?dataset=secondary"
```

## Hackathon Scope

This backend was built for Hackstreet 4.0 (Pentathon 3.0, March 19 2026) addressing Problem Statement 3: AI Knowledge Discovery Engine for Unstructured Data.

It is a hackathon MVP optimized for a stable 2-minute demo, not a production system. Design decisions reflect that priority:

- In-memory storage instead of a database — avoids setup complexity and failure modes
- Pre-baked demo fallback — guarantees the demo works even if live processing is slow
- Curated excerpt PDFs instead of full papers — controls for noise the pipeline cannot yet handle
- Threshold overrides on `/analyze` — allows live tuning without restarting the server
- Background model loading with health check — server starts fast, frontend can poll readiness

The pipeline is real (not mocked). It runs actual sentence transformers and NLI inference on CPU. The demo datasets produce genuine contradictions from real research paper content.
