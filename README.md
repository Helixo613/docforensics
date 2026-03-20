# DocForensics AI

**Automated cross-document contradiction and agreement detection for research papers.**

---

## What Is DocForensics AI?

DocForensics AI is a tool that takes multiple research PDFs on the same topic and automatically finds where they **agree**, where they **contradict**, and which claims are **uncorroborated** (appear in only one paper with no match elsewhere). Every finding is traced back to the exact sentence, document name, and page number.

It is built as a **Flutter mobile app** backed by a **FastAPI + NLP backend**.

---

## Why Does This Exist?

Researchers, analysts, and students regularly review multiple papers on the same subject. The manual process of cross-referencing claims across documents is:

- **Time-consuming** — reading 3-5 papers and mentally tracking which claims overlap or conflict takes hours
- **Error-prone** — contradictions between papers are easy to miss, especially when buried in dense methodology sections
- **Unstructured** — there's no standard way to organize "Paper A says X, but Paper B says the opposite"

DocForensics AI automates this entire workflow. Upload the PDFs, and within seconds you get a structured report of every agreement, contradiction, and solo claim — with page-level citations you can verify.

---

## How It Works — The Full Pipeline

### Stage 1: PDF Text Extraction

**Tool**: PyMuPDF (`fitz`)

Each uploaded PDF is parsed page-by-page. The raw text from every page is extracted and passed to the next stage. If a PDF contains no extractable text (e.g., scanned image PDFs without OCR), it is rejected.

### Stage 2: Sentence Segmentation

**Tool**: spaCy (`en_core_web_sm`)

The extracted text is split into individual sentences using spaCy's statistical sentence boundary detector. Each sentence is tagged with:
- Which document it came from (`doc_name`)
- Which page it was on (`page`)
- A global index across all documents

Whitespace is normalized (multiple spaces/newlines collapsed to single spaces).

### Stage 3: Noise Filtering

Sentences are filtered to remove non-claim content:

| Filter | Rule | Why |
|--------|------|-----|
| Too short | Less than **16 words** | Headings, labels, fragments — not real claims |
| Too long | More than **500 characters** | Run-on extractions, table dumps |
| Numbered references | Starts with `[1]`, `2.`, `3)` etc. | Bibliography entries, list numbering |
| Figures/tables | Starts with "Figure", "Table", "Fig.", "Tab." | Captions, not claims |
| URLs | Contains `http://` or `https://` | Reference links |
| All-caps headers | 15+ characters of only uppercase, spaces, digits | Section headers |
| Pure numbers | Only digits | Page numbers, table values |
| Duplicates | Exact text already seen | Repeated headers/footers |

### Stage 4: Sentence Embeddings

**Model**: `all-MiniLM-L6-v2` (from sentence-transformers)

Every surviving sentence is converted into a **384-dimensional vector** (embedding) that captures its semantic meaning. These vectors are normalized to unit length so that dot products equal cosine similarity.

**Why this model?** MiniLM-L6-v2 is a distilled transformer that balances speed and quality. It produces embeddings where semantically similar sentences have high cosine similarity, even if they use different words.

### Stage 5: Candidate Pair Generation

**Algorithm**: Cosine similarity with top-k selection

For each sentence, we find the **top 3** (`TOP_K = 3`) most similar sentences **from other documents** (same-document pairs are excluded). A pair is only kept if the cosine similarity is above **0.5** (`SIMILARITY_THRESHOLD = 0.5`).

How it works:
1. Compute the full similarity matrix: `embeddings @ embeddings.T`
2. Mask out same-document pairs (set to -2.0)
3. Mask out self-comparisons (diagonal = -2.0)
4. For each sentence, pick the top-k highest-similarity neighbors
5. Deduplicate symmetric pairs (A↔B and B↔A become one pair)
6. Sort by similarity score (highest first)

**Why top-k instead of all pairs?** With N sentences across multiple documents, the number of cross-document pairs grows quadratically. Top-k keeps only the most promising candidates, making NLI classification tractable.

### Stage 6: NLI Classification

**Model**: `cross-encoder/nli-deberta-v3-xsmall` (from HuggingFace)

Each candidate pair is fed into a **Natural Language Inference** (NLI) model. NLI takes two sentences (a premise and a hypothesis) and classifies the relationship as one of:

| NLI Label | Meaning | Example |
|-----------|---------|---------|
| **Entailment** | The two sentences agree / say the same thing | "Transfer learning improves accuracy" ↔ "Pre-trained models boost performance" |
| **Contradiction** | The two sentences directly conflict | "Fine-tuning always helps" ↔ "Fine-tuning can hurt on small datasets" |
| **Neutral** | The sentences are related but don't agree or conflict | "We used ResNet-50" ↔ "The model was trained for 100 epochs" |

The model outputs a softmax probability distribution over these three labels. We take the **highest-scoring label** as the classification.

**Confidence threshold**: Only pairs where the model's confidence is **≥ 0.75** (`CONFIDENCE_THRESHOLD = 0.75`) are kept. Pairs classified as **neutral** are always discarded (they're related but not meaningful findings).

**Why DeBERTa?** DeBERTa-v3-xsmall is a compact cross-encoder that achieves strong NLI accuracy. Cross-encoders process both sentences together (unlike bi-encoders), so they can capture fine-grained semantic relationships like negation, qualification, and scope differences.

### Stage 7: Bucketing

The classified pairs are sorted into three buckets:

| Bucket | What Goes Here | How It's Built |
|--------|---------------|----------------|
| **Contradictions** | Pairs labeled "contradiction" with confidence ≥ 0.75 | Sorted by confidence (highest first) |
| **Agreements** | Pairs labeled "entailment" with confidence ≥ 0.75 | Sorted by confidence (highest first) |
| **Uncorroborated** | Sentences that never appeared in ANY candidate pair | Limited to 30 max (`MAX_UNCORROBORATED = 30`) |

A sentence is "uncorroborated" if it was never matched with any sentence from another document (even below the confidence threshold). These are claims that exist in only one paper.

---

## V2 — The Issue Map Layer

V2 is an **optional synthesis layer** built on top of V1's pair results. Instead of showing individual pairs, it groups related findings into **issues** — higher-level topics where documents agree or disagree.

### Why V2?

V1 gives you a flat list: "Sentence A contradicts Sentence B", "Sentence C agrees with Sentence D", etc. But often multiple pairs are about the same underlying topic. V2 answers: "There are 3 issues in these papers. On Issue 1, papers A and B are on one side, paper C is on the other."

### How V2 Works

#### Step 1: Claim Registry

All unique claims from V1's agreements and contradictions are collected into a registry. Each claim gets a unique ID (`cl_0`, `cl_1`, ...). Duplicate claims (same text, document, page) are merged.

#### Step 2: Connected-Component Grouping

Claims are connected if they appear together in any V1 pair (agreement or contradiction). Using a **graph traversal** (BFS), connected claims are grouped into components. Each component becomes one **issue**.

Example: If claim A contradicts claim B, and claim B agrees with claim C, then A, B, C all belong to the same issue.

#### Step 3: Side Resolution (2-Coloring)

Within each issue, claims are assigned to **sides** using a graph coloring algorithm:

1. Claims connected by **agreement** are merged into blocks (using Union-Find)
2. A contradiction graph is built between blocks
3. The graph is **2-colored** (bipartite coloring): blocks on one side get "Side A", blocks on the other get "Side B"

If 2-coloring fails (the contradiction graph is not bipartite — e.g., A contradicts B, B contradicts C, C contradicts A), all claims are marked as **"mixed"**.

If a block internally contradicts itself (two claims in the same agreement group also contradict each other), all claims are marked as **"mixed"**.

#### Step 4: Issue Status

Each issue gets a status based on its side structure:

| Status | Meaning |
|--------|---------|
| **Contested** | Two clean sides with contradictions between them, no ambiguous claims |
| **Aligned** | One side only, all claims agree, no contradictions |
| **Mixed** | Has sides but also has ambiguous/mixed claims, or documents appear on both sides |
| **Unclear** | No meaningful structure could be determined |

#### Step 5: Quality Signals

Each issue gets a **structural quality** rating:

| Quality | Meaning |
|---------|---------|
| **Clean** | Contested or aligned, no ambiguous claims, no mixed document positions, no merge risk |
| **Borderline** | Has some ambiguous claims or mixed positions, but still has structure |
| **Weak** | No relations, no sides, or status is unclear |

**Merge risk** is flagged when an issue has ≥ 5 claims but the number of relations is ≤ the number of claims. This suggests the issue might be grouping unrelated claims that happen to be loosely connected.

#### Step 6: Fallback Detection

V2 evaluates whether the issue map is actually useful. If it's not, the app recommends falling back to V1's Evidence View. Fallback is triggered if:

| Signal | Trigger |
|--------|---------|
| No structure | Zero issues were formed |
| All unclear | Every issue has "unclear" status |
| Mostly singletons | ≥ 75% of issues contain only 1 claim (when there are ≥ 4 issues) |
| Single incoherent issue | Only 1 issue exists with ≥ 5 claims but it's "mixed" or "unclear" |
| Single dominant issue | One issue contains ≥ 90% of all claims (when ≥ 8 claims) with ≤ 1 resolved issue |

#### Step 7: Coverage Manifest

V2 reports exactly how much of V1's data it covers:

| Metric | What It Measures |
|--------|-----------------|
| `pair_derived_claims_total` | Total unique claims from V1 pairs |
| `pair_derived_claims_represented_in_issues` | How many of those ended up in issues |
| `pair_relations_total` | Total agreement + contradiction relations from V1 |
| `pair_relations_represented_in_issues` | How many relations are captured in issues |
| `structurally_ambiguous_claims_in_issues` | Claims in "mixed" or "unclear" buckets within issues |
| `uncorroborated_claims_outside_issue_map` | V1 uncorroborated claims (these are never in the issue map) |

---

## What Each Value Means in the Results

### V1 Results — Stats

| Field | Meaning |
|-------|---------|
| `total_sentences` | Number of sentences that survived filtering across all documents |
| `candidate_pairs` | Number of cross-document sentence pairs generated (after similarity threshold) |
| `agreements_found` | Number of pairs classified as entailment with confidence ≥ 0.75 |
| `contradictions_found` | Number of pairs classified as contradiction with confidence ≥ 0.75 |
| `uncorroborated_count` | Number of sentences that never appeared in any candidate pair |

### V1 Results — Each Finding

| Field | Meaning |
|-------|---------|
| `id` | Unique identifier (e.g., `c_0` for first contradiction, `a_0` for first agreement) |
| `claim_a` | First sentence in the pair — includes `text`, `doc_name`, `page` |
| `claim_b` | Second sentence in the pair — includes `text`, `doc_name`, `page` |
| `confidence` | NLI model's confidence that this is a contradiction/agreement (0.75 to 1.0) |

### V2 Results — Issue Map

| Field | Meaning |
|-------|---------|
| `issue_id` | Unique identifier (e.g., `issue_0`) |
| `status` | `contested` / `aligned` / `mixed` / `unclear` — see table above |
| `label` | A representative claim excerpt (truncated to 140 chars) that names the issue |
| `label_kind` | Always `representative_claim_excerpt` — the label is taken from the highest-degree claim |
| `structural_quality` | `clean` / `borderline` / `weak` — see table above |
| `merge_risk` | `true` if the issue might be grouping unrelated claims |
| `documents_involved` | List of document names that have claims in this issue |
| `sides` | Side A and/or Side B, each with their documents and claims |
| `mixed_claims` | Claims that couldn't be cleanly assigned to a side |
| `unclear_claims` | Claims with no relations (isolated within the issue) |

### V2 Results — Fallback Signal

| Field | Meaning |
|-------|---------|
| `should_fallback` | `true` if V2 recommends using V1 Evidence View instead |
| `reasons` | List of reason codes (e.g., `mostly_singleton_issues`) |
| `dominant_issue_share` | Fraction of all claims in the largest issue (0.0 to 1.0) |
| `singleton_issue_ratio` | Fraction of issues that contain only 1 claim (0.0 to 1.0) |

---

## Gemini Enrichment (Optional)

If a Gemini API key is configured, the app sends each contradiction and agreement to **Gemini 1.5 Flash** and asks it to explain the finding in plain English. This produces human-readable insights like:

> "These papers disagree on whether fine-tuning pre-trained models improves performance in low-data settings. Paper A found consistent gains, while Paper C observed that models trained from scratch caught up when given sufficient epochs."

If no API key is set, or if Gemini fails, the app works normally — just without AI-generated explanations.

---

## The Frontend

### Upload Screen

- Pick 1-5 PDF files
- Backend health indicator (green = ready, amber = offline)
- "Analyze Documents" button triggers the full pipeline
- "Try Demo Data" button loads pre-computed results without needing a backend
- Shows file names, sizes, and a remove button for each selected file

### Results Screen

Two views, toggled with a switch:

**Evidence View (V1)** — Three tabs:
- **Contradictions** tab: Expandable cards showing each contradicting pair with source citations
- **Agreements** tab: Same format for agreeing pairs
- **Solo** tab: Claims that appeared in only one document

Each tab shows a colored count badge.

**Issue View (V2)** — A scrollable list of issue cards, each showing:
- Issue status chip (contested/aligned/mixed/unclear)
- Quality chip (clean/borderline/weak)
- Merge risk warning (if applicable)
- Document chips showing which papers are involved
- Expandable side blocks (Side A vs Side B) with individual claims
- Source citation for every claim (document name + page number)

If V2's fallback signal fires, a yellow banner recommends switching to Evidence View.

---

## Running on Windows

### Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.10+ | [python.org](https://www.python.org/downloads/) |
| Flutter SDK | 3.x | [flutter.dev](https://docs.flutter.dev/get-started/install/windows/mobile) |
| Android Studio | Latest | [developer.android.com](https://developer.android.com/studio) (for emulator) |
| Git | Any | [git-scm.com](https://git-scm.com/download/win) |

~2GB free disk space needed for ML models (downloaded automatically on first run).

### Step 1: Clone and Checkout

```powershell
git clone https://github.com/Helixo613/docforensics.git
cd docforensics
git checkout Full_version
```

### Step 2: Start the Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Or use the included script:

```powershell
.\scripts\run_backend.ps1 -Port 8000
```

**First run**: Models (~500MB) download automatically. Wait until the terminal shows Uvicorn's startup message. Verify with:

```powershell
curl http://127.0.0.1:8000/health
# Should return: {"status": "ok", "models_loaded": true}
```

### Step 3: Configure the Flutter App

Edit `lib/config/constants.dart`:

```dart
static const String backendBaseUrl = 'http://10.0.2.2:8000';  // for Android emulator
```

| Setup | URL |
|-------|-----|
| Android emulator (backend on same PC) | `http://10.0.2.2:8000` |
| Physical Android device (same WiFi) | `http://YOUR_PC_IP:8000` |
| Chrome / Windows desktop | `http://localhost:8000` |

Find your PC's IP: run `ipconfig` in PowerShell, use the IPv4 address from your WiFi adapter.

### Step 4: Configure Gemini (Optional)

In the same `lib/config/constants.dart`:

```dart
static const String geminiApiKey = 'YOUR_ACTUAL_KEY_HERE';
```

Get a free key at [aistudio.google.com](https://aistudio.google.com). Skip this if you don't need AI explanations.

### Step 5: Run the Flutter App

Open a **second** terminal:

```powershell
# From the repo root (not backend/)
flutter pub get
flutter run
```

### Step 6: Android — Enable HTTP Traffic

Add `android:usesCleartextTraffic="true"` to `android/app/src/main/AndroidManifest.xml`:

```xml
<application
    android:usesCleartextTraffic="true"
    android:label="consensus_brief"
    ...>
```

### Running with WSL Backend

```bash
# Inside WSL
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Port forwarding from Windows (admin PowerShell):

```powershell
netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=$(wsl hostname -I | ForEach-Object { $_.Trim() })
```

WSL's IP changes on restart — re-run the portproxy command after each WSL restart.

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, CORS, router registration
│   │   ├── config.py                # All thresholds and model names
│   │   ├── schemas.py               # V1 Pydantic response models
│   │   ├── v2_schemas.py            # V2 Pydantic response models
│   │   ├── storage.py               # In-memory session store
│   │   ├── routers/
│   │   │   ├── health.py            # GET /health
│   │   │   ├── upload.py            # POST /upload
│   │   │   ├── analyze.py           # POST /analyze/{id}
│   │   │   ├── results.py           # GET /results/{id}
│   │   │   ├── search.py            # GET /search/{id}?q=
│   │   │   ├── demo.py              # GET /demo
│   │   │   └── v2.py                # POST /v2/analyze/{id}, GET /v2/results/{id}
│   │   └── services/
│   │       ├── pdf_extractor.py     # PyMuPDF text extraction
│   │       ├── sentence_splitter.py # spaCy sentence segmentation
│   │       ├── filters.py           # Noise/boilerplate removal
│   │       ├── embeddings.py        # MiniLM-L6-v2 embeddings
│   │       ├── candidate_generation.py  # Cosine similarity top-k
│   │       ├── nli.py               # DeBERTa NLI classification
│   │       ├── bucketing.py         # Sort into agree/contradict/uncorroborated
│   │       ├── search.py            # Semantic search
│   │       ├── pair_analysis.py     # Shared V1 pipeline (used by V1 + V2)
│   │       ├── v2_issue_map.py      # Issue grouping, 2-coloring, quality
│   │       └── demo_loader.py       # Loads frozen demo data
│   ├── tests/
│   │   └── test_v2_issue_map.py     # 8 unit tests for V2
│   ├── scripts/
│   │   ├── run_backend.ps1          # PowerShell launcher
│   │   └── smoke_test.ps1           # PowerShell smoke test
│   ├── demo_papers/                 # 3 demo PDFs (primary set)
│   ├── demo_papers_secondary/       # 3 demo PDFs (secondary set)
│   ├── demo_assets/                 # Synthetic test papers (sample 3 + 4)
│   └── requirements.txt
│
├── lib/                             # Flutter frontend
│   ├── main.dart
│   ├── config/constants.dart        # Backend URL, Gemini key, colors
│   ├── models/
│   │   ├── analysis_result.dart     # V1 data models
│   │   ├── v2_models.dart           # V2 issue map models
│   │   └── session_results.dart     # Wrapper: V1 + optional V2
│   ├── screens/
│   │   ├── upload_screen.dart       # File picker + health status
│   │   └── results_screen.dart      # Evidence/Issue view toggle
│   ├── services/
│   │   ├── api_service.dart         # Backend HTTP client
│   │   └── gemini_service.dart      # Gemini enrichment client
│   └── widgets/
│       ├── finding_card.dart        # V1 evidence cards
│       ├── stats_summary.dart       # Stats row
│       ├── demo_banner.dart         # Demo mode banner
│       └── v2_issue_card.dart       # V2 issue cards
│
├── android/, ios/, web/, windows/   # Platform files
└── pubspec.yaml
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | `{status, models_loaded}` — check if backend is ready |
| `POST` | `/upload` | Upload PDFs (multipart form), returns `{session_id, documents}` |
| `POST` | `/analyze/{session_id}` | Run V1 pipeline, returns agreements/contradictions/uncorroborated |
| `GET` | `/results/{session_id}` | Retrieve cached V1 results |
| `GET` | `/search/{session_id}?q=` | Semantic search across all session claims |
| `GET` | `/demo` | Returns pre-computed demo results |
| `POST` | `/v2/analyze/{session_id}` | Build V2 issue map from V1 results |
| `GET` | `/v2/results/{session_id}` | Retrieve cached V2 results |

Swagger docs: `http://localhost:8000/docs`

---

## Configuration Reference

All tunable parameters live in `backend/app/config.py`:

| Parameter | Value | What It Controls |
|-----------|-------|-----------------|
| `MIN_WORDS` | 16 | Minimum words for a sentence to be kept |
| `MAX_SENTENCE_CHARS` | 500 | Maximum characters for a sentence |
| `TOP_K` | 3 | Number of most-similar cross-doc neighbors per sentence |
| `SIMILARITY_THRESHOLD` | 0.5 | Minimum cosine similarity to form a candidate pair |
| `CONFIDENCE_THRESHOLD` | 0.75 | Minimum NLI confidence to classify as agreement/contradiction |
| `MAX_UNCORROBORATED` | 30 | Cap on uncorroborated claims in output |
| `MAX_FILES` | 10 | Maximum PDFs per upload |
| `MIN_FILES` | 2 | Minimum PDFs per upload |
| `MAX_FILE_SIZE_MB` | 20 | Maximum size per PDF |
| `SPACY_MODEL` | `en_core_web_sm` | spaCy model for sentence splitting |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence embedding model (384-dim) |
| `NLI_MODEL` | `cross-encoder/nli-deberta-v3-xsmall` | NLI classification model |

---

## Running Tests

### V2 Unit Tests (8 tests)

```powershell
cd backend
python -m pytest tests/test_v2_issue_map.py -v
```

### Smoke Test

```powershell
cd backend
.\scripts\smoke_test.ps1 -BaseUrl "http://127.0.0.1:8000"
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Backend not reachable from app | Check URL in `lib/config/constants.dart`. Use `10.0.2.2` for emulator. |
| Android blocks HTTP | Add `android:usesCleartextTraffic="true"` to `AndroidManifest.xml` |
| Port 8000 in use | Use different port: `uvicorn app.main:app --port 8080`, update `constants.dart` |
| Models slow to load | First run downloads ~500MB. Check `GET /health` for `models_loaded` status. |
| WSL IP changed | Re-run `netsh interface portproxy` command. Find IP: `wsl hostname -I` |
| `flutter pub get` fails | Delete `pubspec.lock` and retry. Ensure Flutter SDK is on PATH. |
| PowerShell blocks scripts | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
| HuggingFace `position_ids` warning | Harmless, does not affect results. Ignore it. |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend framework | FastAPI + Uvicorn | REST API server |
| PDF parsing | PyMuPDF | Extract text from PDFs page-by-page |
| Sentence splitting | spaCy (`en_core_web_sm`) | Statistical sentence boundary detection |
| Sentence embeddings | `all-MiniLM-L6-v2` | 384-dim semantic vectors for similarity |
| NLI classification | `cross-encoder/nli-deberta-v3-xsmall` | Contradiction/entailment/neutral classification |
| Frontend | Flutter | Cross-platform mobile app |
| AI enrichment | Gemini 1.5 Flash | Optional human-readable explanations |

---

## Team

Built for **Hackstreet 4.0**.
