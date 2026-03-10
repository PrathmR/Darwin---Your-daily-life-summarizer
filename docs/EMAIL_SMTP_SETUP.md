# 📧 Email & SMTP Configuration Guide

Complete guide to setting up email verification via SMTP for **Darwin**.

---

## Overview

Darwin sends **email verification links** to users after registration. This requires an SMTP server configuration. The default setup uses **Gmail SMTP**, but any SMTP provider can be used.

### What Emails Does the App Send?

| Email Type | Trigger | Content |
|---|---|---|
| **Email Verification** | After user registers with email/password | Contains a tokenized link to verify the email address |

> [!NOTE]
> Google OAuth users do **not** receive verification emails — their email is automatically marked as verified since Google has already verified it.

---

## Gmail SMTP Setup (Recommended for Development)

### Step 1 — Enable 2-Factor Authentication on Your Google Account

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Under **"How you sign in to Google"**, enable **2-Step Verification**
3. Follow the prompts to set it up

> [!IMPORTANT]
> 2-Step Verification **must** be enabled before you can create App Passwords.

### Step 2 — Generate a Gmail App Password

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. You may need to re-enter your Google password
3. In the **"App name"** field, type: `Darwin` (or any name you like)
4. Click **"Create"**
5. Google will show a **16-character app password** (e.g., `abcd efgh ijkl mnop`)
6. **Copy this password** — you won't be able to see it again!

> [!CAUTION]
> Do **not** use your regular Gmail password. App Passwords are separate credentials designed for third-party apps.

### Step 3 — Add to Backend `.env`

```env
# Email / SMTP Configuration
EMAIL_FROM=your-email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop     # The 16-char App Password (no spaces)
SMTP_USE_TLS=true
```

### Step 4 — Configure Frontend URL

The verification email contains a link back to the frontend. Make sure this is set:

```env
FRONTEND_URL=http://localhost:3000
```

The verification link will look like:
```
http://localhost:3000/verify-email?token=<random-secure-token>
```

---

## How Email Verification Works

```
1. User registers with email + password
              │
              ▼
2. Backend creates user (is_email_verified = false)
   and generates a random URL-safe token
              │
              ▼
3. Backend sends email via SMTP with:
   "Click here to verify: {FRONTEND_URL}/verify-email?token={token}"
              │
              ▼
4. User clicks the link in their email
              │
              ▼
5. Frontend opens /verify-email page
   which calls GET /auth/verify-email?token={token}
              │
              ▼
6. Backend finds token in DB, checks expiry (1 hour)
   Sets is_email_verified = true
              │
              ▼
7. User can now log in! ✅
```

### Token Security

- Tokens are generated using `secrets.token_urlsafe(32)` — cryptographically random
- Each token expires after **1 hour**
- Tokens are **single-use** — cleared from the database after verification
- The verification token is stored alongside the user in the database

---

## Using Other SMTP Providers

### Outlook / Office 365

```env
EMAIL_FROM=your-email@outlook.com
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true
```

### Mailtrap (Testing — Emails Don't Actually Deliver)

```env
EMAIL_FROM=test@example.com
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=your-mailtrap-username
SMTP_PASSWORD=your-mailtrap-password
SMTP_USE_TLS=true
```

### Custom SMTP Server

```env
EMAIL_FROM=no-reply@yourdomain.com
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=587
SMTP_USER=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_USE_TLS=true
```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Registration succeeds but no email received | Check SMTP settings. Look at backend terminal for error logs |
| `Authentication failed` SMTP error | For Gmail: ensure you're using an **App Password**, not your regular password |
| `Connection refused` SMTP error | Check `SMTP_HOST` and `SMTP_PORT` are correct |
| Verification link goes to wrong URL | Update `FRONTEND_URL` in backend `.env` to match your frontend address |
| Token expired when clicking link | Tokens expire after 1 hour. Register again to get a new token |
| Gmail blocks "less secure app" access | Google no longer supports this. Use **App Passwords** instead |

---

## Without SMTP (Development Workaround)

If you don't want to set up SMTP for development, you can still use the app:

1. **Google OAuth** sign-in works without SMTP (email is auto-verified)
2. For local accounts, you can manually verify emails in the database:

```bash
sqlite3 backend/auth.db
UPDATE users SET is_email_verified = 1 WHERE email = 'your-email@example.com';
.quit
```

Then restart the backend, and the user can log in without email verification.
