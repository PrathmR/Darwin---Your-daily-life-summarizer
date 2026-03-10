# 📄 Darwin — AI-Powered Meeting Summarizer

## Full Project Documentation

---

## 1. Project Overview

**Darwin** is a full-stack, AI-powered web application that transforms meeting recordings (audio/video files) into structured, actionable summaries. Users upload a meeting recording, and the system automatically transcribes the content, extracts key insights using AI, and generates a downloadable PDF summary — all through a modern, intuitive web interface.

---

## 2. Problem Statement

### The Challenge

In today's remote and hybrid work environment, meetings are a primary mode of communication. However:

- **Information overload:** Professionals attend multiple meetings daily, making it impossible to retain every detail.
- **Manual note-taking is unreliable:** Human notes are subjective, incomplete, and often miss critical decisions or action items.
- **Meeting recordings go unwatched:** Organizations record meetings but rarely revisit lengthy recordings due to time constraints.
- **No structured output:** Even when meetings are summarized, the output lacks consistency — decisions, action items, and key quotes are scattered or lost.
- **Accountability gaps:** Without clear action items and ownership attribution, follow-ups are missed.

### Who Is This For?

- **Corporate teams** that need concise post-meeting reports.
- **Students & researchers** who want to summarize lecture recordings.
- **Project managers** tracking decisions and action items across multiple meetings.
- **Remote teams** spread across time zones who need async meeting digests.

---

## 3. Solution

Darwin solves these problems by providing an **end-to-end automated pipeline** that:

1. **Accepts audio/video uploads** — Supports common meeting recording formats.
2. **Transcribes speech to text** — Uses AssemblyAI's industry-leading speech-to-text API with speaker diarization (who said what).
3. **Extracts intelligence with AI** — Leverages Google's Gemini generative AI to produce:
   - Meeting **topics** and themes
   - Key **decisions** made
   - **Action items** with ownership
   - **Important quotes**
   - **Speaker-by-speaker breakdowns**
   - Identified **issues** and discussion points
4. **Generates a professional PDF report** — A structured, downloadable document summarizing the entire meeting.
5. **Saves all outputs** — Transcripts, JSON data, and PDFs are stored for future reference.

### Key Differentiators

| Feature | Darwin | Manual Notes | Generic Transcription |
|---|---|---|---|
| Automated transcription | ✅ | ❌ | ✅ |
| Speaker identification | ✅ | ❌ | Sometimes |
| AI-extracted action items | ✅ | ❌ | ❌ |
| Decision tracking | ✅ | Partial | ❌ |
| PDF report generation | ✅ | ❌ | ❌ |
| Secure user authentication | ✅ | N/A | Varies |

---

## 4. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                        │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ Landing  │ │   Auth    │ │Dashboard │ │Meeting Upload│  │
│  │  Page    │ │Login/Sign │ │  (Index) │ │& Summarizer  │  │
│  └──────────┘ └───────────┘ └──────────┘ └──────────────┘  │
│         │              │            │             │         │
│         └──────────────┴────────────┴─────────────┘         │
│                        Axios HTTP                           │
│                     Port 3000 (Vite)                        │
└────────────────────────┬────────────────────────────────────┘
                         │  REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI + Uvicorn)                 │
│                      Port 8000                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    API Layer                           │  │
│  │  /auth/*            │    /api/meet-summary            │  │
│  │  - POST /register   │    - POST / (upload file)       │  │
│  │  - POST /login      │                                 │  │
│  │  - POST /refresh    │                                 │  │
│  │  - POST /logout     │                                 │  │
│  │  - POST /google     │                                 │  │
│  │  - GET  /me         │                                 │  │
│  │  - GET  /verify     │                                 │  │
│  └───────────┬─────────┴──────────────┬──────────────────┘  │
│              │                        │                     │
│  ┌───────────▼──────────┐ ┌───────────▼──────────────────┐  │
│  │   Security Layer     │ │      Summarizer Pipeline     │  │
│  │  - Argon2 hashing    │ │  1. Save uploaded file       │  │
│  │  - JWT (access +     │ │  2. Extract audio (MoviePy)  │  │
│  │    refresh tokens)   │ │  3. Transcribe (AssemblyAI)  │  │
│  │  - httpOnly cookies  │ │  4. AI extraction (Gemini)   │  │
│  │  - Google OAuth      │ │  5. Generate PDF (ReportLab) │  │
│  │  - Email verify      │ │  6. Save outputs             │  │
│  └───────────┬──────────┘ └───────────┬──────────────────┘  │
│              │                        │                     │
│  ┌───────────▼────────────────────────▼──────────────────┐  │
│  │                  Data Layer                            │  │
│  │  SQLite (auth.db)  │  File System (uploads/, output/) │  │
│  │  - Users table     │  - uploaded recordings           │  │
│  │  - SQLAlchemy ORM  │  - transcripts (.txt)            │  │
│  │                    │  - summaries (.json)              │  │
│  │                    │  - reports (.pdf)                 │  │
│  └────────────────────┴──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
    ┌──────────┐  ┌───────────┐  ┌─────────┐
    │AssemblyAI│  │Google     │  │Gmail    │
    │  (STT)   │  │Gemini AI  │  │SMTP     │
    └──────────┘  └───────────┘  └─────────┘
```

---

## 5. Technology Stack

### Backend

| Technology | Version | Purpose |
|---|---|---|
| **Python** | 3.10+ | Core programming language |
| **FastAPI** | Latest | Async web framework with auto-generated API docs |
| **Uvicorn** | Latest | ASGI server for running FastAPI |
| **SQLAlchemy** | Latest | ORM for database operations |
| **SQLite** | Built-in | Lightweight relational database (dev) |
| **Pydantic** | v2 | Data validation & serialization |
| **python-jose** | Latest | JWT token creation & verification |
| **Passlib + Argon2** | Latest | Secure password hashing |
| **AssemblyAI SDK** | Latest | Speech-to-text transcription with speaker diarization |
| **Google Generative AI** | Latest | Gemini LLM for intelligent summarization |
| **MoviePy** | Latest | Audio extraction from video files |
| **ReportLab** | Latest | Professional PDF generation |
| **SMTP (smtplib)** | Built-in | Email verification via Gmail |

### Frontend

| Technology | Version | Purpose |
|---|---|---|
| **React** | 18.3 | Component-based UI framework |
| **TypeScript** | 5.5+ | Type-safe JavaScript |
| **Vite** | 5.4 | Fast build tool & dev server |
| **Tailwind CSS** | 3.4 | Utility-first CSS framework |
| **shadcn/ui (Radix)** | Latest | Accessible, composable UI component library |
| **React Router** | 6.x | Client-side routing |
| **TanStack Query** | 5.x | Server state management & caching |
| **Axios** | 1.13 | HTTP client for API communication |
| **React Hook Form + Zod** | Latest | Form management & schema validation |
| **Recharts** | 2.12 | Charting & data visualization |
| **Lucide React** | Latest | Modern icon set |
| **Sonner** | Latest | Toast notifications |
| **Marked** | 15.x | Markdown rendering for AI outputs |

### External Services

| Service | Purpose |
|---|---|
| **AssemblyAI** | Cloud-based speech-to-text transcription |
| **Google Gemini** | Large language model for content extraction & summarization |
| **Google OAuth 2.0** | Social authentication (Sign in with Google) |
| **Gmail SMTP** | Transactional emails (email verification) |

---

## 6. Features

### 🔐 Authentication & Authorization

- **Email/Password registration** with secure Argon2 password hashing
- **Email verification** via SMTP with tokenized verification links
- **JWT-based session management** using httpOnly cookies (access + refresh tokens)
- **Google OAuth 2.0** sign-in integration
- **Protected routes** — dashboard and summarizer are auth-gated
- **Token refresh** — seamless silent token renewal

### 🧠 AI Meeting Summarization

- **File upload** — Accept audio/video meeting recordings
- **Automatic transcription** — AssemblyAI converts speech to text with speaker diarization
- **AI-powered extraction** using Google Gemini:
  - Meeting **topic** identification
  - **Key facts** and structured JSON output (topics, participants, decisions, action items, issues, quotes)
  - **Speaker-by-speaker** summaries
- **PDF report generation** — Professional, downloadable meeting summary document
- **Output storage** — All transcripts, JSONs, and PDFs saved to `output_summaries/`

### 🎨 User Interface

- **Landing page** with feature overview
- **Auth page** — Login / Register with email or Google
- **Dashboard (Index)** — Authenticated user home
- **Create Game / Game Workspace** — Meeting upload and summarization workflow
- **Email verification page** — Token-based email confirmation
- **Responsive design** — Works on desktop and mobile
- **Modern UI** — Built with shadcn/ui components and Tailwind CSS

---

## 7. API Endpoints

### Authentication (`/auth`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user with email & password |
| `GET` | `/auth/verify-email?token=...` | Verify email address |
| `POST` | `/auth/login` | Login with email & password |
| `POST` | `/auth/refresh` | Refresh access token |
| `POST` | `/auth/logout` | Logout and clear cookies |
| `POST` | `/auth/google` | Login/register via Google OAuth |
| `GET` | `/auth/me` | Get current authenticated user |

### Meeting Summary (`/api/meet-summary`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/meet-summary` | Upload a meeting file for transcription & summarization |

---

## 8. Database Schema

### `users` Table

| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-incremented user ID |
| `email` | String (Unique) | User's email address |
| `password_hash` | String (Nullable) | Argon2 password hash (null for Google-only users) |
| `provider` | String | Auth provider: `local` or `google` |
| `google_id` | String (Nullable) | Google account ID |
| `is_email_verified` | Boolean | Whether email is verified |
| `email_verification_token` | String (Nullable) | Token for email verification |
| `email_verification_token_expires_at` | DateTime (Nullable) | Token expiry timestamp |
| `refresh_token_version` | Integer | Versioned refresh tokens for security |
| `created_at` | DateTime | Account creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

---

## 9. Security Measures

| Area | Implementation |
|---|---|
| **Password storage** | Argon2 hashing via Passlib (winner of the Password Hashing Competition) |
| **Session management** | JWT tokens stored in httpOnly, secure cookies (prevents XSS) |
| **Token types** | Separate access (15 min) and refresh (7 days) tokens |
| **Token refresh** | Versioned refresh tokens — logout invalidates all sessions |
| **CORS** | Strict origin allowlist via `BACKEND_CORS_ORIGINS` |
| **Input validation** | Pydantic v2 schema enforcement on all API inputs |
| **Email verification** | Cryptographically random URL-safe tokens with expiry |
| **OAuth security** | Google ID tokens verified server-side |

---

## 10. AI Processing Pipeline

The meeting summarization follows this pipeline:

```
┌────────────┐     ┌──────────────┐     ┌───────────────┐
│ Upload File│────▸│ Extract Audio│────▸│  Transcribe   │
│ (audio/    │     │  (MoviePy)   │     │ (AssemblyAI)  │
│  video)    │     │  if video    │     │ w/ speakers   │
└────────────┘     └──────────────┘     └───────┬───────┘
                                                │
                                                ▼
                                   ┌────────────────────────┐
                                   │   AI Extraction        │
                                   │   (Google Gemini)       │
                                   │                        │
                                   │  • Topics              │
                                   │  • Participants        │
                                   │  • Decisions           │
                                   │  • Action Items        │
                                   │  • Issues Discussed    │
                                   │  • Important Quotes    │
                                   │  • Speaker Summaries   │
                                   └────────────┬───────────┘
                                                │
                          ┌─────────────────────┼─────────────────────┐
                          ▼                     ▼                     ▼
                   ┌────────────┐       ┌──────────────┐      ┌────────────┐
                   │ Save .txt  │       │  Save .json  │      │ Generate   │
                   │ Transcript │       │  Structured  │      │ .pdf Report│
                   └────────────┘       └──────────────┘      └────────────┘
```

The system uses a **dual-key Gemini strategy** — if the primary API key hits rate limits, it automatically falls back to a secondary key.

---

## 11. Frontend Routes

| Route | Page | Auth Required | Description |
|---|---|---|---|
| `/` | `Index` | No | Landing page / dashboard |
| `/auth` | `Auth` | No | Login & registration page |
| `/create-game` | `CreateGame` | ✅ Yes | Meeting upload & summarizer |
| `/game-workspace` | `GameWorkspace` | ✅ Yes | Workspace for results |
| `/verify-email` | `VerifyEmail` | No | Email verification handler |
| `*` | `NotFound` | No | 404 page |

---

## 12. Environment Variables Reference

### Backend (`.env`)

| Variable | Required | Description |
|---|---|---|
| `APP_NAME` | No | Application name (default: `AuthService`) |
| `ENVIRONMENT` | No | Environment mode: `dev` / `prod` |
| `DEBUG` | No | Debug mode flag |
| `DATABASE_URL` | **Yes** | Database connection string |
| `JWT_ACCESS_SECRET` | **Yes** | Secret key for access tokens |
| `JWT_REFRESH_SECRET` | **Yes** | Secret key for refresh tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Access token TTL (default: 15) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | Refresh token TTL (default: 7) |
| `BACKEND_CORS_ORIGINS` | No | Comma-separated allowed origins |
| `FRONTEND_URL` | No | Frontend application URL |
| `EMAIL_FROM` | No | Sender email address |
| `SMTP_HOST` | No | SMTP server hostname |
| `SMTP_PORT` | No | SMTP server port (default: 587) |
| `SMTP_USER` | No | SMTP login username |
| `SMTP_PASSWORD` | No | SMTP login password |
| `SMTP_USE_TLS` | No | Enable TLS for SMTP |
| `GOOGLE_CLIENT_ID` | No | Google OAuth client ID |
| `ASSEMBLYAI_API_KEY` | **Yes*** | AssemblyAI API key |
| `GEMINI_API_KEY_PRIMARY` | **Yes*** | Google Gemini API key |
| `GEMINI_API_KEY_SECONDARY` | No | Fallback Gemini API key |

*\* Required for meeting summarization feature to work.*

### Frontend (`.env`)

| Variable | Required | Description |
|---|---|---|
| `VITE_BACKEND_URL` | **Yes** | Backend base URL (e.g., `http://localhost:8000`) |
| `VITE_API_URL` | **Yes** | Backend API URL (e.g., `http://localhost:8000/api`) |
| `VITE_GOOGLE_CLIENT_ID` | No | Google OAuth client ID for frontend |

---

## 13. Future Scope

- **PostgreSQL** support for production database
- **Cloud deployment** (AWS, GCP, or Azure)
- **Real-time processing** with WebSocket progress updates
- **Team workspaces** — share summaries across team members
- **Calendar integration** — auto-process scheduled meeting recordings
- **Multi-language support** for meeting transcription
- **Summary history** — searchable archive of past meeting summaries
