# 🔐 Google OAuth & JWT Authentication Setup

Complete guide to configuring Google OAuth 2.0 sign-in and JWT token-based authentication for **Darwin**.

---

## Overview

Darwin supports two authentication methods:

1. **Email/Password (Local)** — Users register with email and password. Passwords are hashed with Argon2. Email verification is required.
2. **Google OAuth 2.0** — Users sign in with their Google account. No password is needed.

Both methods issue **JWT tokens** stored in **httpOnly cookies** for session management.

---

## Part 1: JWT Token Setup

JWT (JSON Web Tokens) are used for session management. The app uses two separate tokens:

| Token | Purpose | Default Expiry | Cookie Name |
|---|---|---|---|
| **Access Token** | Authenticates API requests | 15 minutes | `access_token` |
| **Refresh Token** | Issues new access tokens silently | 7 days | `refresh_token` |

### Step 1 — Generate JWT Secrets

Each token type needs its own secret key. Generate them using Python:

```bash
python -c "import secrets; print(secrets.token_hex(64))"
```

Run this command **twice** — once for each secret.

### Step 2 — Add to Backend `.env`

```env
# JWT Secrets (REQUIRED — must be unique and kept private!)
JWT_ACCESS_SECRET=<paste-first-generated-secret-here>
JWT_REFRESH_SECRET=<paste-second-generated-secret-here>

# Token Expiry (optional — defaults shown)
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

> [!CAUTION]
> **Never commit your JWT secrets to Git.** The `.env` file should be in `.gitignore`. If secrets are leaked, all existing user sessions become compromised.

### How JWT Works in This App

```
User Login/Register
        │
        ▼
┌───────────────────┐
│ Backend verifies   │
│ credentials        │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐     httpOnly cookies
│ Create JWT tokens  │────────────────────▶  Browser stores cookies
│ (access + refresh) │                       automatically
└───────────────────┘

        ... time passes ...

┌───────────────────┐     access_token cookie
│ Browser makes API  │────────────────────▶  Backend validates JWT
│ request            │                       from cookie
└───────────────────┘

        ... access token expires (15 min) ...

┌───────────────────┐     refresh_token cookie
│ Frontend calls     │────────────────────▶  Backend issues new
│ /auth/refresh-token│                       access token
└───────────────────┘
```

### Security Features

- **Argon2 password hashing** — Winner of the Password Hashing Competition, resistant to GPU/ASIC attacks
- **httpOnly cookies** — Tokens cannot be read by JavaScript (prevents XSS attacks)
- **Versioned refresh tokens** — Logging out increments the version, invalidating all old refresh tokens
- **Separate secrets** — Compromising one token type doesn't compromise the other

---

## Part 2: Google OAuth 2.0 Setup

### Step 1 — Go to Google Cloud Console

Open [Google Cloud Console](https://console.cloud.google.com/) and sign in with your Google account.

### Step 2 — Create a Project (if you don't have one)

1. Click the project dropdown at the top of the page
2. Click **"New Project"**
3. Enter a project name (e.g., `Darwin`)
4. Click **"Create"**

### Step 3 — Configure the OAuth Consent Screen

1. Navigate to **APIs & Services → OAuth consent screen**
2. Select **"External"** user type and click **"Create"**
3. Fill in the required fields:
   - **App name:** `Darwin` (or your choice)
   - **User support email:** Your email
   - **Developer contact email:** Your email
4. Click **"Save and Continue"**
5. On the **Scopes** page, add these scopes:
   - `openid`
   - `email`
   - `profile`
6. Click **"Save and Continue"** through the remaining steps

### Step 4 — Create OAuth 2.0 Credentials

1. Navigate to **APIs & Services → Credentials**
2. Click **"+ CREATE CREDENTIALS" → "OAuth client ID"**
3. Select **"Web application"** as the application type
4. Set the name (e.g., `Darwin Web Client`)
5. Under **"Authorized JavaScript origins"**, add:
   ```
   http://localhost:3000
   ```
6. Under **"Authorized redirect URIs"**, add:
   ```
   http://localhost:3000
   ```
7. Click **"Create"**

### Step 5 — Copy the Client ID

After creation, you'll see a dialog with your:
- **Client ID** — `xxxxx.apps.googleusercontent.com`
- **Client Secret** — (not needed for this app, we use ID token verification)

Copy the **Client ID**.

### Step 6 — Add to Environment Variables

**Backend `.env`** (in `backend/`):

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

**Frontend `.env`** (in `frontend/`):

```env
VITE_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

> [!IMPORTANT]
> The **same Client ID** must be used in both backend and frontend `.env` files. The backend verifies the Google ID token against this Client ID.

### How Google OAuth Works in This App

```
1. User clicks "Sign in with Google" on frontend
                    │
                    ▼
2. Google shows consent screen in popup
                    │
                    ▼
3. User approves → Google returns an ID token (credential)
                    │
                    ▼
4. Frontend sends the credential to POST /auth/google
                    │
                    ▼
5. Backend verifies the token with Google's servers
   using google.oauth2.id_token.verify_oauth2_token()
                    │
                    ▼
6. Backend creates/finds user, issues JWT cookies
                    │
                    ▼
7. User is logged in! 🎉
```

### Account Linking

If a user already has a local (email/password) account and later signs in with Google using the **same email**, the accounts are automatically linked:
- The existing account gets the `google_id` attached
- The provider is updated to `google`
- Email is automatically marked as verified

---

## Quick Reference — Auth Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register with email + password |
| `GET` | `/auth/verify-email?token=...` | Verify email via token link |
| `POST` | `/auth/login` | Login with email + password |
| `POST` | `/auth/google` | Login/register via Google OAuth |
| `POST` | `/auth/refresh-token` | Refresh access token |
| `POST` | `/auth/logout` | Logout (clear cookies) |
| `GET` | `/auth/me` | Get current authenticated user |

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Google sign-in popup doesn't appear | Check `VITE_GOOGLE_CLIENT_ID` is set correctly in `frontend/.env` |
| `Invalid Google token` error | Ensure `GOOGLE_CLIENT_ID` in backend `.env` matches the frontend's `VITE_GOOGLE_CLIENT_ID` |
| `Google client ID not configured` error | Add `GOOGLE_CLIENT_ID` to your backend `.env` file |
| JWT tokens not working after restart | JWT secrets haven't changed — tokens should persist. Check that `.env` is loading correctly |
| `401 Not authenticated` errors | Access token may have expired. The frontend should automatically call `/auth/refresh-token` |
| Cookies not being sent in requests | Ensure `BACKEND_CORS_ORIGINS` includes your frontend URL and CORS is configured with `allow_credentials=True` |
