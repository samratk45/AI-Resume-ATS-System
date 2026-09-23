# AI-Resume-ATS-System

An AI-powered resume analyzer that scores resumes the way an Applicant Tracking System (ATS) would, gives detailed, actionable feedback, and can compare a resume against a specific job description for a targeted match score.

Live app: Streamlit frontend → FastAPI backend (Railway) → Supabase (auth + history) → Groq (LLM parsing)

---

## Features

- **General ATS Score** — uploads a resume (PDF/DOCX) and returns an overall ATS compatibility score out of 100, broken down into five weighted components.
- **Job Description Comparison** — pastes a job description alongside the resume for a targeted match score, missing-keyword analysis, and a skills gap report.
- **Detailed, actionable feedback** — every issue found includes severity, ATS impact, where it appears in the resume, how to fix it, and concrete before/after suggestions.
- **Skill validation** — cross-references listed skills against the resume's actual project and experience descriptions, flagging skills with no supporting evidence.
- **Hyperlink & contact extraction** — pulls email, phone, LinkedIn, and GitHub links out of both the visible text and embedded PDF/DOCX hyperlinks.
- **PDF report export** — generates a downloadable, styled PDF report of any analysis.
- **Analysis history** — signed-in users' past analyses are saved to Supabase and browsable/deletable from the app.
- **Authentication** — Supabase email/password auth; the backend independently verifies each request's JWT (supports both `ES256`/JWKS and `HS256` signing).

---

## Architecture

```
┌─────────────────┐        HTTPS         ┌──────────────────────┐
│  Streamlit App   │ ───────────────────► │   FastAPI Backend     │
│  (frontend/)      │ ◄─────────────────── │   (backend/)           │
└─────────────────┘      JSON / files     └──────────┬────────────┘
        │                                             │
        │ Supabase Auth (sign in/up)                  │ JWT verification (JWKS / HS256)
        ▼                                             ▼
┌─────────────────┐                         ┌──────────────────────┐
│    Supabase       │ ◄────────────────────  │   Supabase REST API    │
│  (auth + Postgres) │      save/read history │   (analyses table)      │
└─────────────────┘                         └──────────────────────┘
                                                        │
                                                        ▼
                                              ┌──────────────────────┐
                                              │       Groq API          │
                                              │  (LLM resume/JD parsing) │
                                              └──────────────────────┘
```

**Analysis pipeline, per request:**

1. Resume file (PDF/DOCX, max 5 MB) is uploaded and validated (`python-magic` MIME check).
2. Text is extracted (`pdfplumber` → `PyPDF2` fallback for PDFs; `python-docx` for DOCX), including embedded hyperlinks.
3. The raw text is sent to **Groq** (`openai/gpt-oss-120b`) to extract structured data — skills, experience, projects, education, action verbs, keywords.
4. **spaCy** (`en_core_web_sm`) and **Sentence-Transformers** (`all-MiniLM-L6-v2`) handle NLP tasks: entity recognition, semantic similarity, and skill-to-project validation via embeddings.
5. If a job description was provided, it's parsed the same way and compared against the resume for a match score.
6. Scores, issues, and recommendations are computed and returned as JSON; if the user is signed in, the result is also saved to Supabase in the background.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io/) |
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn |
| NLP | [spaCy](https://spacy.io/) (`en_core_web_sm`), [Sentence-Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) |
| LLM parsing | [Groq](https://groq.com/) (`openai/gpt-oss-120b`) |
| Auth & Database | [Supabase](https://supabase.com/) (Auth + Postgres, accessed via REST) |
| File parsing | `pdfplumber`, `PyPDF2`, `python-docx`, `python-magic` |
| PDF report generation | `Jinja2` + `WeasyPrint` |
| Deployment | Docker on [Railway](https://railway.app/) (backend), [Streamlit Community Cloud](https://streamlit.io/cloud) (frontend) |

---

## Project Structure

```
AI-Resume-ATS-System/
├── backend/
│   ├── main.py                    # FastAPI app, lifespan model loading, CORS
│   ├── api/
│   │   ├── auth.py                # JWT verification (JWKS + HS256)
│   │   └── routes.py              # All API endpoints
│   ├── core/
│   │   └── config.py              # Environment-driven configuration
│   ├── database/
│   │   └── supabase_db.py         # Async Supabase REST client (save/read/delete history)
│   ├── models/
│   │   └── schemas.py             # Pydantic response models
│   ├── services/
│   │   ├── resume_parser.py       # File validation + text/hyperlink extraction
│   │   ├── groq_parser.py         # LLM-based resume/JD structured extraction
│   │   ├── resume_analyzer.py     # Orchestrates the full analysis pipeline
│   │   ├── ats_scorer.py          # Scoring logic (formatting, keywords, content, etc.)
│   │   ├── jd_matcher.py          # Resume ↔ job description comparison
│   │   ├── feedback_engine.py     # Issue detection + human-readable feedback
│   │   ├── recommendation_engine.py
│   │   ├── report_generator.py    # HTML report rendering (Jinja2)
│   │   └── pdf_export.py          # HTML → PDF (WeasyPrint)
│   └── utils/
│       ├── file_utils.py
│       └── matching.py
├── frontend/
│   ├── streamlit_app.py           # Entry point / page router
│   ├── views/                     # landing, scorer, history, resources
│   ├── components/                # Reusable UI pieces (score display, feedback, etc.)
│   └── services/
│       ├── api_client.py          # Wraps calls to the FastAPI backend
│       └── supabase_client.py     # Frontend Supabase auth client
├── Dockerfile                     # Backend container definition
├── requirements.txt                # Combined backend + frontend dependencies
└── .env                            # Local-only secrets (never committed)
```

---

## Getting Started

### Prerequisites

- Python 3.12
- A [Supabase](https://supabase.com/) project (free tier is fine)
- A [Groq](https://console.groq.com/) API key

### Local Setup

```bash
git clone https://github.com/samratk45/AI-Resume-ATS-System.git
cd AI-Resume-ATS-System

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Environment Variables

Create a `.env` file at the project root:

```dotenv
# Supabase
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_ANON_KEY=your-anon-public-key
SUPABASE_JWT_SECRET=your-jwt-secret        # only needed if your project issues HS256 tokens

# Groq
GROQ_API_KEY=your-groq-api-key

# Optional overrides
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
```
---


## API Reference

All endpoints except `/health` require a Supabase JWT: `Authorization: Bearer <access_token>`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/analyze-resume` | Upload a resume (+ optional job description) and get a full analysis |
| `GET` | `/api/v1/health` | Health check — confirms NLP/embedding models are loaded |
| `GET` | `/api/v1/history` | Get the signed-in user's past analyses |
| `DELETE` | `/api/v1/history/{analysis_id}` | Delete one saved analysis |
| `POST` | `/api/v1/generate-pdf` | Generate a downloadable PDF report from an analysis result |
| `GET` | `/api/v1/history/{analysis_id}/pdf` | Generate a PDF report for a saved history entry |

Full interactive documentation (request/response schemas, try-it-out) is available at `/docs` (Swagger UI) on any running instance.
