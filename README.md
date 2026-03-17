# SafeWaves

**AI-Powered Multi-Threat Cyber Defense Platform**

> Detect. Analyze. Explain. Defend. — All from one unified dashboard.

IndiaNext Hackathon 2026 | BuildStorm Track

**Live Demo:** [Frontend (Vercel)](https://safewaves.vercel.app) | [Backend API (Render)](https://safewaves-api.onrender.com/docs)

---

## Problem Statement & Relevance

Cyber attackers are increasingly using AI tools to create more believable scams, evade detection, and automate attacks. Organizations need intelligent systems that not only detect such attacks but also justify their decisions — showing what made something suspicious, what evidence was used, how confident the system is, and what action should be taken next.

SafeWaves is a **unified, multi-threat cyber defense platform** covering **6 real-world threat domains** with AI/ML-powered detection, **explainable AI** at every layer, and **actionable recommendations** — all accessible through a single interface.

### Why This Matters

- **Phishing** remains the #1 attack vector — responsible for 36% of data breaches (Verizon DBIR 2024)
- **Deepfakes** used in fraud have grown 3000% year-over-year
- **Prompt injection** is an emerging threat with no standardized defense as LLMs are widely deployed
- **AI-generated content** undermines trust in digital information at scale
- Security teams need **explainable** detections, not just binary alerts

---

## Core Modules

### 1. Threat Input Module

The system accepts 6 distinct input types, each validated with Pydantic schemas:

| Input Type | Endpoint | What It Accepts |
|---|---|---|
| Email text + subject | `POST /api/v1/analyze/email` | Email body text and subject line |
| URL string | `POST /api/v1/analyze/url` | Any URL for analysis |
| Image file | `POST /api/v1/analyze/deepfake` | Multipart image upload (JPEG/PNG) |
| Prompt text | `POST /api/v1/analyze/prompt` | LLM prompt or text input |
| Login event history | `POST /api/v1/analyze/behavior` | JSON array of login events with timestamps, IPs, locations, devices |
| Text content | `POST /api/v1/analyze/ai-content` | Any text block for AI authorship analysis |

### 2. Detection Module (6 Independent ML Analyzers)

Each module uses custom feature engineering followed by weighted heuristic scoring. Every detector also has an architectural hook (`_predict_with_model`) to accept a pre-trained sklearn pipeline, falling back to heuristics if unavailable.

| Module | Features Extracted | Detection Techniques |
|---|---|---|
| **Phishing Email** | 11 features: urgency keywords, suspicious phrases, URL count, HTML detection, caps ratio, typo-squatting (10 brands with 3-5 typo variants each), emotional manipulation (fear/greed/curiosity lexicons), link-text mismatch, sender impersonation, subject urgency | NLP feature extraction + weighted scoring |
| **Malicious URL** | 18 features: URL length, dot/hyphen count, IP detection, HTTPS, suspicious TLD (18 TLDs), subdomain count, path/query/fragment length, port detection, digit ratio, special chars, Shannon entropy, URL shortener detection (11 services), suspicious keywords (16), typo-squatting via Levenshtein distance (10 brands) | Lexical URL analysis + entropy + edit distance |
| **Deepfake Detection** | 8 features: ELA mean/std/max, Laplacian noise level, color histogram uniformity, face region anomaly, JPEG quality estimate, edge consistency | Error Level Analysis (ELA) + Laplacian noise + Sobel edge detection. Generates a base64 heatmap overlay |
| **Prompt Injection** | 10 features: pattern matches, instruction overrides, role switches, system extraction attempts, delimiter injection, encoding attacks (with base64 decode validation), jailbreak patterns, text length, uppercase ratio, special char density | 13 compiled regex patterns across 7 attack categories. Returns character offsets for UI highlighting |
| **Behavior Anomaly** | 8 features: unusual hour ratio (1-5 AM), impossible travel (33 city-pair distance table, 1000 km/h max speed), device diversity, failed login ratio, TOR exit node matching (12 prefixes), rapid-fire logins (<60s apart), new location ratio, IP diversity | Statistical anomaly detection across temporal, geospatial, and device dimensions |
| **AI Content Detection** | 10 features: avg sentence length, sentence length variance, vocabulary richness (type-token ratio), punctuation diversity, transition word density (27 words), hedge word density (18 words), trigram repetition, burstiness (coefficient of variation), avg word length, passive voice ratio | Linguistic fingerprint analysis comparing against AI-typical feature ranges |

### 3. Explainability Module (Three-Layer System)

**Layer 1 — SHAP-Style Feature Attribution** (`backend/app/services/explainer.py`):
- Computes per-feature contribution values (feature_value * weight = contribution)
- Returns top 5 features sorted by absolute contribution
- Classifies each factor's impact: "negative" (increases risk), "positive" (increases safety), "neutral"
- 94-line `FEATURE_DESCRIPTIONS` dict with human-readable explanations for all features across all 6 modules

**Layer 2 — Natural Language Explanation** (`backend/app/services/gemini_service.py`):
- Uses `gemini-2.0-flash` to generate plain-English explanations incorporating threat type, risk score, and top SHAP contributors
- Full template-based fallback per threat type (high/medium/low tiers) when the API is unavailable

**Layer 3 — Structured Key Factors**:
- Each factor includes: feature name, observed value, impact direction, and human-readable description
- Visualized in the frontend via SHAP bar charts, risk gauges, confidence meters, and severity badges

### 4. Response & Recommendation Module (`backend/app/services/recommendation.py`)

- 5-6 specific, actionable recommendations per threat type (all 6 types covered)
- Each recommendation has: action text, priority level (immediate/high/medium/low), detailed description, and minimum severity threshold
- Priority escalation logic: for critical/high severity, priorities are automatically bumped up
- Returns 3-5 sorted recommendations per analysis
- Generic fallback recommendations when no specific pool matches

### 5. User Interface / Dashboard

| Page | Route | Purpose |
|---|---|---|
| Landing | `/` | Hero, threat module cards, workflow explanation, explainability overview |
| Dashboard | `/dashboard` | Stats cards (total analyzed, threats detected, safety rate, active modules), risk gauges, recent threats list |
| Analyze | `/analyze` | 6-tab analysis interface with appropriate input forms per module, full result display |
| Threat Feed | `/threat-feed` | Auto-refreshing (10s polling) aggregated threat list with type/severity filtering, expandable cards |
| Adversarial Test | `/adversarial` | Module selection, sample data loading, side-by-side original vs adversarial comparison with risk gauges |

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT (React + Vite)                        │
│                                                                     │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌──────────────────┐   │
│  │ Dashboard  │ │  Analyze  │ │  Threat   │ │   Adversarial    │   │
│  │  (stats,   │ │ (6 tabs,  │ │   Feed    │ │    Testing       │   │
│  │  gauges,   │ │  inputs,  │ │ (real-time│ │ (robustness      │   │
│  │  recent)   │ │  results) │ │  filtered)│ │  validation)     │   │
│  └───────────┘ └───────────┘ └───────────┘ └──────────────────┘   │
│         │              │             │               │              │
│         └──────────────┴─────────────┴───────────────┘              │
│                         Axios + Vite Proxy                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │ /api/v1/*
┌────────────────────────────┴────────────────────────────────────────┐
│                        SERVER (FastAPI)                              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    API Router (8 endpoints)                   │   │
│  │  /analyze/email  /analyze/url  /analyze/deepfake             │   │
│  │  /analyze/prompt /analyze/behavior /analyze/ai-content       │   │
│  │  /threat-feed    /adversarial-test                           │   │
│  └───────────────────────────┬──────────────────────────────────┘   │
│                              │                                      │
│  ┌──────────────┐  ┌────────┴───────┐  ┌───────────────────────┐   │
│  │  6 ML/AI     │  │  Explainability │  │  Recommendation      │   │
│  │  Analyzers   │  │  Engine         │  │  Engine               │   │
│  │              │  │                 │  │                       │   │
│  │  - Email     │  │  - SHAP-style   │  │  - Context-aware     │   │
│  │  - URL       │  │    feature      │  │    prioritized       │   │
│  │  - Deepfake  │  │    attribution  │  │    actions           │   │
│  │  - Prompt    │  │  - Gemini API   │  │  - Severity-based    │   │
│  │  - Behavior  │  │    NL explain   │  │    escalation        │   │
│  │  - AI Content│  │  - Risk scoring │  │  - Per-threat-type   │   │
│  └──────────────┘  └────────────────┘  └───────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   Threat Store (In-Memory)                    │   │
│  │        Aggregates all analysis results for the feed           │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Separation of Concerns

- **API Layer** — Request validation (Pydantic), routing, response formatting
- **ML Model Layer** (`backend/app/models/ml/`) — 6 independent detector classes, each with feature extraction + scoring
- **Service Layer** (`backend/app/services/`) — Explainer, risk scorer, Gemini service, recommendation engine, threat store
- **Schema Layer** (`backend/app/models/schemas.py`) — Unified Pydantic models for all requests and responses
- **Frontend Pages** (`frontend/src/pages/`) — 5 page components
- **Shared Components** (`frontend/src/components/shared/`) — GlassCard, RiskGauge, SeverityBadge, ConfidenceMeter, GradientButton, LoadingSpinner
- **Results Components** (`frontend/src/components/results/`) — ResultPanel, ShapVisualization, ExplanationCard, RecommendationCard
- **State Management** (`frontend/src/store/useStore.js`) — Zustand global store

---

## Risk Scoring System (`backend/app/services/risk_scorer.py`)

| Score Range | Severity |
|---|---|
| 80-100 | Critical |
| 60-79 | High |
| 40-59 | Medium |
| 20-39 | Low |
| 0-19 | Safe |

Confidence estimation uses: score extremity (weight 0.30), feature signal strength (weight 0.25), ambiguity penalty (40-60 zone, -0.15), base confidence (0.35), and a +0.10 bonus for decisive scores (>80 or <20).

---

## Adversarial Robustness Testing

- Endpoint: `POST /api/v1/adversarial-test`
- Supports 4 modules: email, url, prompt, ai_content
- Applies adversarial transformations (e.g., appending legitimacy phrases to phishing emails, wrapping injections in innocent context)
- Runs both original and adversarial inputs through the full pipeline
- Compares classification stability: `robust = original.is_threat == adversarial.is_threat`
- Frontend shows side-by-side comparison with risk gauges

---

## Tech Stack

### Backend
| Component | Technology |
|---|---|
| API Framework | FastAPI (Python 3.12) |
| ML/Analysis | Custom feature-based heuristic models per threat type |
| Image Analysis | Pillow (ELA, Laplacian, Sobel) + NumPy |
| Explainability | Custom SHAP-style attribution engine |
| LLM Integration | Google Gemini 2.0 Flash (optional, with full local fallback) |
| Validation | Pydantic v2 |
| Deployment | Render (Procfile + render.yaml) |

### Frontend
| Component | Technology |
|---|---|
| Framework | React 19 + Vite 8 |
| Styling | Tailwind CSS v4 (glassmorphism dark theme) |
| Animations | Framer Motion |
| State | Zustand |
| HTTP Client | Axios |
| Deployment | Vercel (vercel.json) |

---

## Project Structure

```
safewaves/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── router.py                 # Central API router (8 endpoints)
│   │   │   └── endpoints/
│   │   │       ├── email.py              # POST /analyze/email
│   │   │       ├── url.py                # POST /analyze/url
│   │   │       ├── deepfake.py           # POST /analyze/deepfake
│   │   │       ├── prompt.py             # POST /analyze/prompt
│   │   │       ├── behavior.py           # POST /analyze/behavior
│   │   │       ├── ai_content.py         # POST /analyze/ai-content
│   │   │       ├── threat_feed.py        # GET  /threat-feed
│   │   │       └── adversarial.py        # POST /adversarial-test
│   │   ├── models/
│   │   │   ├── schemas.py                # Pydantic request/response models
│   │   │   └── ml/
│   │   │       ├── phishing_model.py     # Phishing email detector (11 features)
│   │   │       ├── url_model.py          # Malicious URL detector (18 features)
│   │   │       ├── deepfake_model.py     # Deepfake image detector (8 features, ELA)
│   │   │       ├── prompt_model.py       # Prompt injection detector (10 features)
│   │   │       ├── behavior_model.py     # Behavior anomaly detector (8 features)
│   │   │       └── ai_content_model.py   # AI content detector (10 features)
│   │   ├── services/
│   │   │   ├── explainer.py              # SHAP-style explainability engine
│   │   │   ├── risk_scorer.py            # Risk scoring + confidence estimation
│   │   │   ├── recommendation.py         # Context-aware recommendation engine
│   │   │   ├── gemini_service.py         # Gemini API integration (optional)
│   │   │   └── threat_store.py           # In-memory threat aggregation (deque, max 100)
│   │   ├── config.py                     # Environment configuration
│   │   └── main.py                       # FastAPI application entry
│   ├── data/uploads/                     # Temporary file uploads
│   ├── requirements.txt
│   └── Procfile                          # Render deployment command
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── shared/                   # GlassCard, RiskGauge, SeverityBadge, ConfidenceMeter, GradientButton, LoadingSpinner
│   │   │   └── results/                  # ResultPanel, ShapVisualization, ExplanationCard, RecommendationCard
│   │   ├── pages/
│   │   │   ├── Landing.jsx               # Landing page
│   │   │   ├── Dashboard.jsx             # Stats + recent threats
│   │   │   ├── Analyze.jsx               # 6-tab analysis interface
│   │   │   ├── ThreatFeed.jsx            # Real-time threat feed
│   │   │   └── AdversarialTest.jsx       # Adversarial robustness testing
│   │   ├── services/api.js              # Axios API client
│   │   └── store/useStore.js            # Zustand global state
│   ├── vercel.json                       # Vercel deployment config
│   └── vite.config.js                    # Vite + proxy configuration
├── render.yaml                           # Render deployment config
├── .gitignore
└── README.md
```

---

## API Reference

All endpoints are prefixed with `/api/v1`.

| Method | Endpoint | Request Body | Description |
|---|---|---|---|
| `POST` | `/analyze/email` | `{ "email_text": "...", "subject": "..." }` | Phishing email analysis |
| `POST` | `/analyze/url` | `{ "url": "https://..." }` | Malicious URL analysis |
| `POST` | `/analyze/deepfake` | `multipart/form-data (file)` | Deepfake image analysis |
| `POST` | `/analyze/prompt` | `{ "text": "..." }` | Prompt injection detection |
| `POST` | `/analyze/behavior` | `{ "login_history": [...] }` | Behavior anomaly analysis |
| `POST` | `/analyze/ai-content` | `{ "text": "..." }` | AI content detection |
| `GET` | `/threat-feed` | — | Aggregated threat feed |
| `POST` | `/adversarial-test` | `{ "module": "...", "input_data": {...} }` | Adversarial robustness test |
| `GET` | `/health` | — | Health check |

### Unified Response Schema (AnalysisResponse)

Every analysis endpoint returns a consistent structure:

```json
{
  "id": "uuid",
  "timestamp": "2026-03-16T14:30:00Z",
  "threat_type": "phishing",
  "risk_score": 87,
  "severity": "critical",
  "is_threat": true,
  "confidence": 0.92,
  "explanation": {
    "summary": "This email shows strong indicators of a phishing attack...",
    "key_factors": [
      { "feature": "urgency_keywords", "value": "5", "impact": "negative", "description": "High count of urgency/fear-inducing words" }
    ],
    "shap_data": { "features": [...], "values": [...], "base_value": 0.5 }
  },
  "recommendations": [
    { "action": "Block sender", "priority": "immediate", "description": "..." }
  ],
  "extra_data": { ... }
}
```

---

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm 9+

### Backend

```bash
cd safewaves/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd safewaves/frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`. Vite proxy forwards `/api` requests to the backend.

### Environment Variables (Optional)

Create a `.env` file in `backend/`:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
DEBUG=false
```

---

## Deployment

- **Backend** — Render (configured via `render.yaml` + `Procfile`)
- **Frontend** — Vercel (configured via `vercel.json` with API rewrites to backend)

---

## What's Implemented vs What's Missing

### Implemented (Judging Criteria Coverage)

| Criterion | Status | Notes |
|---|---|---|
| Problem Relevance & Impact (15 marks) | DONE | 6 real-world threat domains, practical use case |
| Technical Complexity (15 marks) | DONE | 6 modules, clean architecture, custom feature engineering (Shannon entropy, Levenshtein, ELA, impossible travel) |
| Explainable AI Quality (15 marks) | DONE | Three-layer system: SHAP attribution + Gemini NL + key factors. Frontend visualization with charts, gauges, badges |
| Cybersecurity Depth (15 marks) | DONE | All 6 threat areas, adversarial testing, risk scoring, defense recommendations |
| Innovation & Trend Alignment (10 marks) | DONE | Deepfake + prompt injection + AI content detection + adversarial testing |
| Prototype Quality & Usability (10 marks) | DONE | Polished glassmorphism UI, 5 pages, animations, responsive |
| Presentation & Demo (5 marks) | -- | No presentation file exists yet |

### Bonus Areas (up to 10 marks)

| Bonus Area | Status |
|---|---|
| Adversarial robustness testing | DONE (4/6 modules) |
| Privacy-preserving design | DONE (ephemeral processing, no PII, no persistent storage) |
| Responsible AI safeguards | PARTIAL (explainability and confidence scores present; no bias testing or user feedback loop) |
| Real-time alerting | PARTIAL (10s polling only, no WebSocket/SSE) |
| Deployment readiness | DONE (live on Render + Vercel) |
| Multi-modal threat fusion | NOT DONE (modules operate independently, no cross-module correlation) |
| Secure-by-design | DONE (CORS, input validation, file type restrictions) |

---

## GAPS TO ADDRESS

### Critical (Mandatory Deliverables)

1. **Presentation file (.pptx)** — Required deliverable. Must cover: problem understanding, proposed solution, architecture, AI/ML approach, explainability method, cybersecurity relevance, demo results, and future scope.

2. **Visual architecture diagram** — Problem statement asks for "a visual diagram showing all modules and how data flows through your system." The ASCII diagram in this README is not sufficient. Need a proper `.png` or `.svg` diagram.

3. **Short report / documentation** — Problem statement asks for "a brief document covering your project title, team details, problem addressed, solution overview, approach used, explainability method, and innovation highlights." The README covers content but a standalone document may be expected.

### High Priority (Scoring Impact)

4. **No real trained ML models (AI/ML Effectiveness — 15 marks at risk)** — All 6 detectors use hand-crafted weighted heuristic scoring. There are no trained models, no training data, no model evaluation metrics. The `_predict_with_model` hooks exist but no sklearn pipelines are loaded. The problem statement explicitly says: *"a simple input-to-label model is not sufficient. Depth, pipeline, and integration are expected."* While the feature engineering is deep, the lack of any actual trained model could cost marks. Even a simple trained sklearn model on one or two modules would strengthen the narrative significantly.

5. **Multi-modal threat fusion not implemented** — Listed as both an innovation expectation and a bonus criterion. Modules operate completely independently. There is no cross-module correlation, compound risk scoring, or unified threat assessment combining signals from multiple modules.

6. **Adversarial testing only supports 4/6 modules** — Behavior and deepfake modules have no adversarial transform functions defined in the backend.

### Medium Priority (Bonus Marks / Polish)

7. **Real-time alerting is polling only** — 10-second `setInterval` polling. No WebSocket or SSE. Adding WebSocket support would be a visible improvement for judges.

8. **Threat store is ephemeral (in-memory deque, max 100)** — Restarting the backend loses all history. No persistent database. Dashboard stats reset on restart. This could be noticeable during a live demo if the backend restarts.

9. **No rate limiting on the API** — A security platform with no rate limiting on its own endpoints is a notable omission.

10. **Landing page cards look AI-generated** — The `SurfaceCard` component on the landing page uses a generic style that doesn't match the polished dashboard cards. Should be restyled to match the dashboard's `glass-card` style for visual consistency.

---

## License

MIT
