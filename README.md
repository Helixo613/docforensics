# DocForensics AI

Cross-document contradiction and agreement detector with evidence tracing.

Upload research PDFs, and the system finds where papers agree, contradict, or make uncorroborated claims — with page-level citations back to the source text.

## What This Is

**V1 (Evidence View)** — the core product. Sentence-level NLI (Natural Language Inference) compares claims across documents and classifies each pair as agreement, contradiction, or neutral. Every finding links back to exact text, document name, and page number.

**V2 (Issue Map)** — optional synthesis layer. Groups V1's pair-level findings into higher-level "issues" using connected-component analysis over the agreement/contradiction graph. Adds structural quality signals, merge-risk flags, and fallback detection. If V2 produces weak structure, the frontend recommends falling back to V1.

V1 is always the default. V2 is additive and non-destructive.

---

## Project Structure

```
.
├── backend/                    # FastAPI + NLP pipeline
│   ├── app/
│   │   ├── main.py             # App entry, CORS, router registration
│   │   ├── config.py           # Thresholds, model names
│   │   ├── schemas.py          # V1 Pydantic models
│   │   ├── v2_schemas.py       # V2 Pydantic models
│   │   ├── storage.py          # In-memory session store
│   │   ├── routers/
│   │   │   ├── health.py       # GET /health
│   │   │   ├── upload.py       # POST /upload
│   │   │   ├── analyze.py      # POST /analyze/{session_id}
│   │   │   ├── results.py      # GET /results/{session_id}
│   │   │   ├── search.py       # GET /search/{session_id}?q=
│   │   │   ├── demo.py         # GET /demo
│   │   │   └── v2.py           # POST /v2/analyze, GET /v2/results
│   │   ├── services/
│   │   │   ├── pdf_extractor.py
│   │   │   ├── sentence_splitter.py
│   │   │   ├── filters.py
│   │   │   ├── embeddings.py
│   │   │   ├── candidate_generation.py
│   │   │   ├── nli.py
│   │   │   ├── bucketing.py
│   │   │   ├── search.py
│   │   │   ├── pair_analysis.py      # Shared V1 analysis logic
│   │   │   ├── v2_issue_map.py       # Issue grouping + quality
│   │   │   └── demo_loader.py
│   │   └── utils/
│   │       └── model_loader.py       # Background model loading
│   ├── demo_papers/            # Primary demo PDFs
│   ├── demo_papers_secondary/  # Secondary demo PDFs
│   ├── demo_session.json       # Frozen primary demo output
│   ├── demo_session_2.json     # Frozen secondary demo output
│   ├── demo_assets/            # Synthetic papers for V2 testing
│   ├── scripts/
│   │   ├── run_backend.ps1     # Windows PowerShell launcher
│   │   └── smoke_test.ps1      # PowerShell smoke test
│   ├── tests/
│   │   └── test_v2_issue_map.py
│   └── requirements.txt
├── lib/                        # Flutter frontend
│   ├── main.dart
│   ├── config/constants.dart
│   ├── models/
│   │   ├── analysis_result.dart
│   │   ├── v2_models.dart
│   │   └── session_results.dart
│   ├── screens/
│   │   ├── upload_screen.dart
│   │   └── results_screen.dart
│   ├── services/
│   │   ├── api_service.dart
│   │   └── gemini_service.dart
│   └── widgets/
│       ├── finding_card.dart
│       ├── stats_summary.dart
│       ├── demo_banner.dart
│       └── v2_issue_card.dart
└── pubspec.yaml
```

---

## Setup

### Prerequisites

- Python 3.10+ (backend)
- Flutter SDK (frontend)
- ~2GB disk for ML models (downloaded on first run)

### 1. Backend Setup

#### On WSL (recommended for development)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Use `--host 0.0.0.0` so the backend is reachable from Windows/emulators.

#### On Windows (native PowerShell)

```powershell
cd backend
.\scripts\run_backend.ps1 -Port 8000
```

Or manually:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

If port 8000 is occupied, use any free port (e.g., 8080).

#### First-run behavior

Models download on first startup (~1-2 min). `GET /health` returns `models_loaded: false` until ready. The app handles this — just wait.

You may see a HuggingFace warning about `position_ids` for the NLI model. This is harmless and does not affect results.

### 2. Frontend Setup

```bash
# From the repo root (not backend/)
flutter pub get
flutter run
```

### 3. Configure Backend URL

Edit `lib/config/constants.dart`:

```dart
static const String backendBaseUrl = 'http://YOUR_BACKEND:8000';
```

| Scenario | URL |
|----------|-----|
| Android emulator → WSL backend | `http://10.0.2.2:8000` |
| Android emulator → Windows backend | `http://10.0.2.2:8000` |
| Physical device → same WiFi | `http://192.168.x.x:8000` (your machine's IP) |
| iOS simulator | `http://localhost:8000` |
| WSL backend from Windows | `http://localhost:8000` (if port-forwarded) |

#### WSL Port Forwarding (if running backend in WSL, frontend on Windows)

```powershell
# Run in admin PowerShell on Windows
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=$(wsl hostname -I | ForEach-Object { $_.Trim() })
```

Note: WSL IP changes on restart. Re-run the portproxy command after WSL restarts.

### 4. Configure Gemini (optional)

In `lib/config/constants.dart`:

```dart
static const String geminiApiKey = 'YOUR_GEMINI_API_KEY';
```

If left as the placeholder, Gemini enrichment is silently skipped. Results still work without it.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Model loading status |
| POST | `/upload` | Upload PDFs, get session_id |
| POST | `/analyze/{session_id}` | Run V1 pair analysis |
| GET | `/results/{session_id}` | Cached V1 results |
| GET | `/search/{session_id}?q=` | Semantic search over session |
| GET | `/demo` | Frozen demo results |
| POST | `/v2/analyze/{session_id}` | Run V2 issue map (requires V1 first) |
| GET | `/v2/results/{session_id}` | Cached V2 results |

Interactive API docs at `http://localhost:8000/docs` once backend is running.

---

## App Flow

```
Upload Screen → pick 1-5 PDFs
    ↓
POST /upload → session_id
    ↓
POST /analyze/{session_id} → V1 pair results
    ↓
POST /v2/analyze/{session_id} → V2 issue map (optional, non-fatal if fails)
    ↓
Gemini enrichment (optional, non-fatal if no key)
    ↓
Results Screen
  ├── Evidence View (V1): Contradictions / Agreements / Solo tabs
  └── Issue Map (V2): Grouped issues with sides, quality, fallback warnings
```

If backend fails at any step, the app falls back to `/demo` and shows a banner.

---

## Verification

### Backend smoke test (PowerShell)

```powershell
cd backend
.\scripts\smoke_test.ps1 -BaseUrl "http://127.0.0.1:8000" -SkipLive
```

### V2 unit tests

```bash
cd backend
python -m pytest tests/test_v2_issue_map.py -v
```

Or without pytest:

```bash
cd backend
python -m unittest tests.test_v2_issue_map -v
```

### Quick manual check

```bash
# Health
curl http://localhost:8000/health

# Demo
curl http://localhost:8000/demo | python -m json.tool
```

---

## Troubleshooting

**Backend not reachable from Flutter app**
- Check the URL in `lib/config/constants.dart`
- Ensure backend is running with `--host 0.0.0.0` (not just `127.0.0.1`) if connecting from emulator/device
- For Android: add `android:usesCleartextTraffic="true"` to `android/app/src/main/AndroidManifest.xml`

**WSL IP changed after restart**
- Re-run the `netsh interface portproxy` command with the new WSL IP
- Find current WSL IP: `wsl hostname -I`

**Port already in use**
- Use a different port: `uvicorn app.main:app --port 8080`
- Update `constants.dart` to match

**Flutter packages not resolving**
- Run `flutter pub get` from the repo root
- If lock file issues: delete `pubspec.lock` and re-run `flutter pub get`

**Models slow to load**
- First run downloads ~500MB of models. Subsequent runs use cache
- Check progress: `GET /health` → `models_loaded` field

---

## Tech Stack

- **Backend**: FastAPI, PyMuPDF, spaCy, sentence-transformers (MiniLM-L6-v2), cross-encoder (nli-deberta-v3-xsmall)
- **Frontend**: Flutter, Google Fonts, file_picker
- **Optional**: Gemini API for AI-enriched summaries
