# 📚 Darwin — Documentation

Welcome to the documentation for **Darwin — AI-Powered Meeting Summarizer**.

---

## 📖 Setup Guides

Follow these guides **in order** to set up the project from scratch:

| # | Guide | Description |
|---|---|---|
| 1 | [**Project Setup Guide**](./PROJECT_SETUP_GUIDE.md) | Full installation & running guide (backend + frontend) |
| 2 | [**Database Setup**](./DATABASE_SETUP.md) | SQLite configuration, schema reference, PostgreSQL migration |
| 3 | [**Google Auth & JWT Setup**](./GOOGLE_AUTH_AND_JWT_SETUP.md) | Google OAuth 2.0 configuration and JWT token setup |
| 4 | [**API Keys Setup**](./API_KEYS_SETUP.md) | Obtaining and configuring AssemblyAI & Google Gemini keys |
| 5 | [**Email & SMTP Setup**](./EMAIL_SMTP_SETUP.md) | Gmail SMTP / App Password configuration for email verification |

---

## 📄 Reference Documentation

| Document | Description |
|---|---|
| [**Project Documentation**](./PROJECT_DOCUMENTATION.md) | Full project overview — architecture, tech stack, features, API reference |
| [**How to Run (Quick Reference)**](./How%20to%20run.txt) | Original quick-start commands |

---

## ⚡ Quick Start

Already have everything configured? Here's how to run the project:

### Terminal 1 — Backend
```bash
cd backend
.\venv\Scripts\Activate.ps1          # Windows PowerShell
uvicorn app.main:app --reload
```

### Terminal 2 — Frontend
```bash
cd frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

---

## 🗂️ Environment Variables Summary

The app requires `.env` files in both `backend/` and `frontend/` directories:

### Backend `.env` (All Variables)

```env
# App
APP_NAME=AuthService
ENVIRONMENT=dev
DEBUG=true

# Database
DATABASE_URL=sqlite:///./auth.db

# JWT (REQUIRED)
JWT_ACCESS_SECRET=<generate-with-python>
JWT_REFRESH_SECRET=<generate-with-python>
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000
FRONTEND_URL=http://localhost:3000

# Email / SMTP
EMAIL_FROM=your-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=<gmail-app-password>
SMTP_USE_TLS=true

# Google OAuth
GOOGLE_CLIENT_ID=<from-google-cloud-console>

# AI API Keys (REQUIRED for summarization)
ASSEMBLYAI_API_KEY=<from-assemblyai-dashboard>
GEMINI_API_KEY_PRIMARY=<from-google-ai-studio>
GEMINI_API_KEY_FALLBACK=<optional-backup-key>
```

### Frontend `.env`

```env
VITE_BACKEND_URL=http://localhost:8000
VITE_API_URL=http://localhost:8000/api
VITE_GOOGLE_CLIENT_ID=<same-as-backend>
```
