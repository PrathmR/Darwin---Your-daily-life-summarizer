# 🔑 API Keys Setup Guide

Complete guide to obtaining and configuring all external API keys required by **Darwin**.

---

## Overview

Darwin requires API keys from two external services for its core meeting summarization feature:

| Service | Purpose | Required? |
|---|---|---|
| **AssemblyAI** | Speech-to-text transcription with speaker diarization | ✅ Yes |
| **Google Gemini** | AI-powered summarization and fact extraction | ✅ Yes (primary key) |
| **Google Gemini (Fallback)** | Backup key if primary hits rate limits | ❌ Optional |

> [!NOTE]
> These API keys are only needed for the **meeting summarization** feature. The auth system (login, register, Google sign-in) works without them.

---

## 1. AssemblyAI API Key

AssemblyAI provides the speech-to-text transcription engine with speaker identification.

### Step 1 — Create an Account

1. Go to [https://www.assemblyai.com/](https://www.assemblyai.com/)
2. Click **"Get Started Free"** or **"Sign Up"**
3. Sign up with your email or Google account

### Step 2 — Get Your API Key

1. After signing in, you'll be taken to the **Dashboard**
2. Your API key is displayed right on the dashboard homepage
3. Click the **copy** icon to copy the key

> Or navigate to: **Dashboard → API Key** (visible at the top of the dashboard)

### Step 3 — Paste in Backend `.env`

Open `backend/.env` and add:

```env
ASSEMBLYAI_API_KEY=your-assemblyai-api-key-here
```

### Pricing & Limits

- **Free tier:** 100 hours of transcription (generous for development/testing)
- Pay-as-you-go after free tier: ~$0.37/hour
- More info: [AssemblyAI Pricing](https://www.assemblyai.com/pricing)

---

## 2. Google Gemini API Key

Google Gemini is used for AI-powered content extraction — summarization, fact extraction, topic identification, and speaker breakdowns.

### Step 1 — Go to Google AI Studio

1. Open [https://aistudio.google.com/](https://aistudio.google.com/)
2. Sign in with your Google account

### Step 2 — Create an API Key

1. Click **"Get API Key"** in the left sidebar (or top menu)
2. Click **"Create API Key"**
3. Select your Google Cloud project (or create a new one)
4. Your API key will be generated — **copy it immediately**

> [!TIP]
> You can also access this at [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Step 3 — Paste in Backend `.env`

```env
# Primary Gemini key (REQUIRED)
GEMINI_API_KEY_PRIMARY=your-gemini-api-key-here

# Fallback key (OPTIONAL — used if primary key hits rate limits)
GEMINI_API_KEY_FALLBACK=your-second-gemini-key-here
```

### Dual-Key Strategy

The app uses a **dual-key fallback** strategy:

```
API Request
    │
    ▼
Try GEMINI_API_KEY_PRIMARY
    │
    ├── Success? ──▶ Return result ✅
    │
    └── Failed (rate limit / error)?
            │
            ▼
        Try GEMINI_API_KEY_FALLBACK
            │
            ├── Success? ──▶ Return result ✅
            │
            └── Both failed ──▶ Return fallback text ⚠️
```

**Why two keys?** Google Gemini has rate limits on free-tier API keys. Having a fallback key reduces the chance of failed summarizations during heavy usage.

### How to Get a Second Key

Simply repeat Step 2 using a **different Google Cloud project**, or create a second key in the same project (different key, same project).

### Pricing & Limits

- **Free tier:** Generous free usage with rate limits (requests per minute)
- The app uses `gemini-2.5-flash` model (fast and efficient)
- More info: [Google AI Pricing](https://ai.google.dev/pricing)

---

## Complete `.env` Template

Here's the complete API keys section for your `backend/.env` file:

```env
# ============================================
# 🔑 AI API KEYS
# ============================================

# AssemblyAI — Speech-to-text transcription (REQUIRED)
# Get from: https://www.assemblyai.com/dashboard
ASSEMBLYAI_API_KEY=your-assemblyai-api-key

# Google Gemini — AI summarization (REQUIRED)
# Get from: https://aistudio.google.com/apikey
GEMINI_API_KEY_PRIMARY=your-primary-gemini-key

# Google Gemini — Fallback key (OPTIONAL)
# Used when primary key hits rate limits
GEMINI_API_KEY_FALLBACK=your-fallback-gemini-key
```

---

## Verifying Your Keys Work

### Quick Test — Backend Startup

After adding your keys, start the backend:

```bash
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

- ✅ If the server starts without errors → keys are loaded correctly
- ❌ `Missing ASSEMBLYAI_API_KEY` error → AssemblyAI key is missing or empty
- ❌ `Missing GEMINI_API_KEY_PRIMARY` error → Gemini primary key is missing or empty

### Full Test — Upload a Meeting File

1. Start both backend and frontend
2. Login / register and navigate to the meeting upload page
3. Upload a short audio file (e.g., a 1-minute `.mp3`)
4. The app will:
   - Transcribe the audio (AssemblyAI) → verifies your AssemblyAI key
   - Summarize the transcript (Gemini) → verifies your Gemini key
   - Generate a PDF report

---

## Security Best Practices

> [!CAUTION]
> **Never commit API keys to version control (Git).** Always use `.env` files and ensure `.env` is listed in `.gitignore`.

- ✅ Store keys in `backend/.env` (which is git-ignored)
- ✅ Use `backend/.example.env` as a template (no real keys)
- ❌ Never hardcode keys in Python source files
- ❌ Never share keys in chat, email, or public repos

### If a Key is Compromised

1. **AssemblyAI:** Go to Dashboard → Regenerate key
2. **Google Gemini:** Go to [Google AI Studio](https://aistudio.google.com/apikey) → Delete and create a new key
3. Update `backend/.env` with the new key
4. Restart the backend

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `❌ Missing ASSEMBLYAI_API_KEY` | Add `ASSEMBLYAI_API_KEY` to `backend/.env` |
| `❌ Missing GEMINI_API_KEY_PRIMARY` | Add `GEMINI_API_KEY_PRIMARY` to `backend/.env` |
| Transcription fails | Check that your AssemblyAI key is correct and has free credits remaining |
| Summarization returns empty/fallback text | Gemini rate limit hit — wait a minute or add a fallback key |
| `Gemini error: 403` | API key may be invalid or the Gemini API is not enabled for your GCP project |
| `.env` changes not taking effect | Restart the backend server after editing `.env` |
