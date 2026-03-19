# Consensus Brief — Flutter App

A Flutter MVP that uploads research PDFs to a backend, analyzes claim agreements and contradictions, then refines the findings with Gemini AI into human-readable insights.

---

## Project Structure

```
lib/
├── main.dart                    # App entry point + theme
├── config/
│   └── constants.dart           # API URLs, keys, colors
├── models/
│   └── analysis_result.dart     # All data models
├── services/
│   ├── api_service.dart         # Backend HTTP calls
│   └── gemini_service.dart      # Gemini enrichment
├── screens/
│   ├── upload_screen.dart       # Screen 1: file picker
│   └── results_screen.dart      # Screen 2: tabbed results
└── widgets/
    ├── finding_card.dart         # Contradiction/agreement cards
    ├── stats_summary.dart        # Top-level stats row
    └── demo_banner.dart          # Yellow demo mode banner
```

---

## Setup

### 1. Install dependencies

```bash
cd consensus_brief
flutter pub get
```

### 2. Configure your backend URL

In `lib/config/constants.dart`:

```dart
static const String backendBaseUrl = 'http://YOUR_BACKEND_IP:8000';
```

- On Android emulator → `http://10.0.2.2:8000`
- On iOS simulator → `http://localhost:8000`
- On physical device → your machine's local IP e.g. `http://192.168.1.x:8000`

### 3. Configure Gemini API key

In `lib/config/constants.dart`:

```dart
static const String geminiApiKey = 'YOUR_GEMINI_API_KEY';
```

Get a free key at [aistudio.google.com](https://aistudio.google.com).

> If you leave it as `YOUR_GEMINI_API_KEY`, Gemini enrichment is silently skipped and raw results are still shown.

### 4. Run

```bash
flutter run
```

---

## App Flow

```
App opens
  ↓
Upload Screen
  ↓  User picks 1–5 PDFs
POST /upload  →  get session_id
  ↓
POST /analyze/{session_id}
  ↓  on timeout/failure
GET /demo  (demo mode fallback)
  ↓
Gemini enrichment (optional)
  ↓
Results Screen (3 tabs)
  - Contradictions
  - Agreements
  - Solo claims
```

---

## Backend API Expected

| Method | Path                    | Response            |
|--------|-------------------------|---------------------|
| GET    | `/health`               | `HealthResponse`    |
| POST   | `/upload`               | `UploadResponse`    |
| POST   | `/analyze/{session_id}` | `AnalysisResult`    |
| GET    | `/results/{session_id}` | `AnalysisResult`    |
| GET    | `/demo`                 | `AnalysisResult`    |

All response shapes are documented in `lib/models/analysis_result.dart`.

---

## Android Network Config

For Android, add `android:usesCleartextTraffic="true"` to your `AndroidManifest.xml` if your backend is on `http://` (not `https://`):

```xml
<application
    android:usesCleartextTraffic="true"
    ...>
```

---

## Key Design Decisions

- **Demo fallback**: if backend fails at any step, app calls `/demo` automatically and shows a banner
- **Gemini is optional**: if no key is set, or if Gemini fails, results are shown without AI insights
- **Expand/collapse cards**: all finding cards are collapsed by default for scannability
- **Tabs with counts**: each tab shows a colored badge with the finding count
