# 🚀 Project Setup & Running Guide

A complete guide to installing, configuring, and running the **Darwin — AI Meeting Summarizer** project on your local machine.

---

## 📋 Prerequisites

| Requirement | Minimum Version | How to Check |
|---|---|---|
| **Python** | 3.10+ | `python --version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **Git** | Any | `git --version` |

> [!NOTE]
> The backend uses **Uvicorn** (ASGI server) and the frontend uses **Vite** as the development server. Both must run simultaneously for the app to work.

---

## 📁 Project Structure Overview

```
Final_Build_V1/
├── backend/                 # FastAPI Backend (Python)
│   ├── app/
│   │   ├── api/routes/      # API route handlers (auth, meet_summary)
│   │   ├── core/            # Config & security (JWT, Argon2)
│   │   ├── db/              # Database session management
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic (summarizer, meet processing)
│   │   ├── email.py         # Email verification via SMTP
│   │   └── main.py          # FastAPI app entry point
│   ├── uploads/             # Uploaded meeting files (auto-created)
│   ├── output_summaries/    # Generated summary outputs
│   ├── .env                 # Environment variables (DO NOT COMMIT)
│   ├── .example.env         # Template for .env
│   └── requirements.txt     # Python dependencies
│
├── frontend/                # React Frontend (TypeScript)
│   ├── src/
│   │   ├── components/      # UI components (shadcn/ui + custom)
│   │   ├── pages/           # Route pages (Auth, Dashboard, CreateGame, etc.)
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utility functions
│   │   ├── App.tsx          # Router & app shell
│   │   └── main.tsx         # React DOM entry point
│   ├── public/              # Static assets
│   ├── .env                 # Frontend environment variables
│   ├── package.json         # Node dependencies & scripts
│   ├── vite.config.ts       # Vite configuration
│   └── tailwind.config.ts   # Tailwind CSS configuration
│
└── How to run.txt           # Quick-start reference
```

---

## 🔧 Part 1: Backend Setup (FastAPI + Python)

### Step 1 — Clone & Navigate

```bash
git clone <repository-url>
cd Final_Build_V1/backend
```

### Step 2 — Create a Virtual Environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (CMD)
python -m venv venv
.\venv\Scripts\activate.bat

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

> You should see `(venv)` at the beginning of your terminal prompt, confirming the virtual environment is active.

### Step 3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies installed:**

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn[standard]` | ASGI server |
| `sqlalchemy` | ORM for database |
| `python-jose[cryptography]` | JWT token handling |
| `passlib[argon2]` + `argon2-cffi` | Password hashing (Argon2) |
| `google-generativeai` | Google Gemini AI for summarization |
| `assemblyai` | Audio/video transcription |
| `moviepy` | Video → audio extraction |
| `reportlab` | PDF generation |
| `python-dotenv` | Environment variable loading |
| `google-auth`, `google-auth-oauthlib` | Google OAuth integration |
| `email-validator` | Email validation |

### Step 4 — Configure Environment Variables

Copy the example and fill in your values:

```bash
cp .example.env .env
```

Edit `.env` with the following variables:

```env
# App Settings
APP_NAME=AuthService
ENVIRONMENT=dev
DEBUG=true

# Database (SQLite for development)
DATABASE_URL=sqlite:///./auth.db

# JWT Secrets (generate your own secure secrets!)
JWT_ACCESS_SECRET=<your-secure-random-secret>
JWT_REFRESH_SECRET=<your-secure-random-secret>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS & Frontend URL
BACKEND_CORS_ORIGINS=http://localhost:3000
FRONTEND_URL=http://localhost:3000

# Email / SMTP Configuration
EMAIL_FROM=yourapp@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# Google OAuth (optional — get from Google Cloud Console)
GOOGLE_CLIENT_ID=your-google-client-id

# AI API Keys (required for meeting summarization)
ASSEMBLYAI_API_KEY=your-assemblyai-api-key
GEMINI_API_KEY_PRIMARY=your-gemini-api-key
GEMINI_API_KEY_SECONDARY=your-backup-gemini-key   # optional fallback
```

> [!IMPORTANT]
> **To generate JWT secrets**, run:
> ```bash
> python -c "import secrets; print(secrets.token_hex(64))"
> ```
> Run it twice — once for `JWT_ACCESS_SECRET` and once for `JWT_REFRESH_SECRET`.

> [!TIP]
> For Gmail SMTP, you need to use an **App Password** (not your regular Gmail password). Go to [Google App Passwords](https://myaccount.google.com/apppasswords) to generate one.

### Step 5 — Run the Backend Server

```bash
uvicorn app.main:app --reload
```

The backend will start at: **http://localhost:8000**

- **API Docs (Swagger):** http://localhost:8000/docs
- **API Docs (ReDoc):** http://localhost:8000/redoc

> [!NOTE]
> The `--reload` flag enables hot-reloading during development. The SQLite database (`auth.db`) is auto-created on first run.

---

## 🎨 Part 2: Frontend Setup (React + TypeScript + Vite)

### Step 1 — Navigate to Frontend

```bash
cd Final_Build_V1/frontend
```

### Step 2 — Install Node Dependencies

```bash
npm install
```

This installs all packages from `package.json`, including:

| Package | Purpose |
|---|---|
| `react` + `react-dom` | UI framework |
| `react-router-dom` | Client-side routing |
| `@tanstack/react-query` | Data fetching & caching |
| `axios` | HTTP client for API calls |
| `@radix-ui/*` | Accessible UI primitives (shadcn/ui) |
| `tailwindcss` | Utility-first CSS |
| `lucide-react` | Icon library |
| `react-hook-form` + `zod` | Form handling & validation |
| `recharts` | Data visualization |
| `sonner` | Toast notifications |
| `marked` | Markdown rendering |

### Step 3 — Configure Environment Variables

Create/edit the `.env` file in the `frontend/` directory:

```env
# Backend API URL
VITE_BACKEND_URL=http://localhost:8000
VITE_API_URL=http://localhost:8000/api

# Google OAuth Client ID (same as backend, from Google Cloud Console)
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

> [!IMPORTANT]
> All frontend environment variables **must** start with `VITE_` to be accessible in the browser. This is a Vite requirement.

### Step 4 — Run the Frontend Dev Server

```bash
npm run dev
```

The frontend will start at: **http://localhost:3000**

---

## ▶️ Running the Full Application

You need **two terminal windows** running simultaneously:

### Terminal 1 — Backend

```bash
cd Final_Build_V1/backend
.\venv\Scripts\Activate.ps1    # or `source venv/bin/activate` on macOS/Linux
uvicorn app.main:app --reload
```

### Terminal 2 — Frontend

```bash
cd Final_Build_V1/frontend
npm run dev
```

Then open your browser to: **http://localhost:3000**

---

## 🏗️ Building for Production

### Frontend Production Build

```bash
cd frontend
npm run build
```

This outputs optimized static files to the `dist/` folder, ready for deployment.

### Backend Production

For production, run without `--reload` and with a production-ready ASGI server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError` in Python | Ensure virtual environment is activated (`(venv)` visible in prompt) |
| CORS errors in browser | Verify `BACKEND_CORS_ORIGINS` in backend `.env` matches the frontend URL |
| `❌ Missing ASSEMBLYAI_API_KEY` error | Add your AssemblyAI API key to backend `.env` |
| Frontend can't reach backend | Confirm backend is running on port 8000 and `VITE_BACKEND_URL` is correct |
| Google OAuth not working | Ensure `GOOGLE_CLIENT_ID` is configured in **both** backend and frontend `.env` files |
| Email verification not sending | Check SMTP settings; for Gmail, use an App Password |
| `sqlite3.OperationalError` | Delete `auth.db` and restart the backend to recreate the database |
| Port 3000 already in use | Kill the existing process or change the port in `vite.config.ts` |

---

## 📝 Available npm Scripts (Frontend)

| Command | Description |
|---|---|
| `npm run dev` | Start the Vite development server on port 3000 |
| `npm run build` | Create a production build in `dist/` |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Run ESLint on the codebase |

---

## 🔗 Useful Links

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Vite Docs:** https://vitejs.dev
- **shadcn/ui:** https://ui.shadcn.com
- **AssemblyAI:** https://www.assemblyai.com
- **Google Generative AI:** https://ai.google.dev
