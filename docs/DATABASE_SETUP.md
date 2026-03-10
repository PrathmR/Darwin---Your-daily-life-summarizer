# 🗄️ Database Setup Guide

Complete guide to setting up the database for **Darwin — AI Meeting Summarizer**.

---

## Overview

Darwin uses **SQLite** as its default database via **SQLAlchemy ORM**. The database file (`auth.db`) is auto-created when the backend starts for the first time — no manual database installation is needed for development.

---

## Quick Start (Default — SQLite)

### Step 1 — Configure the Database URL

Open (or create) the `.env` file in the `backend/` directory and set:

```env
DATABASE_URL=sqlite:///./auth.db
```

This tells SQLAlchemy to create a file called `auth.db` in the `backend/` folder.

### Step 2 — Start the Backend

```bash
cd backend
.\venv\Scripts\Activate.ps1        # Windows PowerShell
# OR
source venv/bin/activate            # macOS / Linux

uvicorn app.main:app --reload
```

On first run, `auth.db` is **automatically created** with all required tables. You should see the file appear in `backend/`.

### Step 3 — Verify

Open a terminal and confirm the file exists:

```bash
# Windows
dir backend\auth.db

# macOS / Linux
ls -la backend/auth.db
```

---

## Database Schema

The application has a single `users` table:

| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK, auto-increment) | Unique user identifier |
| `email` | String (Unique, Indexed) | User's email address |
| `password_hash` | String (Nullable) | Argon2 hash of the password. Null for Google-only users |
| `provider` | String | Auth provider: `local` or `google` |
| `google_id` | String (Nullable) | Google account sub-ID (for OAuth users) |
| `is_email_verified` | Boolean | Whether the email has been verified |
| `email_verification_token` | String (Nullable) | One-time token for email verification |
| `email_verification_token_expires_at` | DateTime (Nullable) | Expiry timestamp for verification token |
| `refresh_token_version` | Integer | Versioned refresh tokens for secure session management |
| `created_at` | DateTime | Account creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

---

## How It Works Under the Hood

### Auto-Table Creation

In `backend/app/main.py`, this single line creates all tables on startup:

```python
Base.metadata.create_all(bind=engine)
```

This uses SQLAlchemy's `create_all()` which is **idempotent** — it only creates tables that don't already exist, so it's safe to run every time the backend starts.

### Session Management

The database session is managed in `backend/app/db/session.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

Each API request gets its own database session through FastAPI's dependency injection.

---

## Common Operations

### Reset the Database

If you need a fresh start (e.g., schema changed, corrupted data):

```bash
# 1. Delete the database file
del backend\auth.db          # Windows
# OR
rm backend/auth.db           # macOS / Linux

# 2. Restart the backend — tables are recreated automatically
uvicorn app.main:app --reload
```

> [!CAUTION]
> Deleting `auth.db` erases **all user accounts and data permanently**. Only do this in development.

### View Database Contents

You can inspect the SQLite database using any of these tools:

- **DB Browser for SQLite** (GUI) — [Download](https://sqlitebrowser.org/)
- **VS Code Extension** — Install "SQLite Viewer" or "SQLite" extension
- **Command Line:**

```bash
# Open SQLite CLI
sqlite3 backend/auth.db

# List tables
.tables

# View all users
SELECT * FROM users;

# Exit
.quit
```

---

## Upgrading to PostgreSQL (Production)

For production deployments, you may want to switch to PostgreSQL:

### Step 1 — Install PostgreSQL and the Python driver

```bash
pip install psycopg2-binary
```

### Step 2 — Update `DATABASE_URL` in `.env`

```env
DATABASE_URL=postgresql://username:password@localhost:5432/darwin
```

### Step 3 — Create the database

```bash
# Using psql CLI
createdb darwin
```

### Step 4 — Restart the backend

The tables will be auto-created on the new PostgreSQL database.

> [!NOTE]
> For production, consider using **Alembic** for proper database migrations instead of `create_all()`.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `sqlite3.OperationalError: unable to open database file` | Check that the `backend/` directory has write permissions |
| `sqlite3.OperationalError: table already exists` | This shouldn't happen since `create_all()` is idempotent. Delete `auth.db` and restart |
| `sqlalchemy.exc.OperationalError: no such column` | Schema has changed. Delete `auth.db` and restart to recreate with the new schema |
| Database file is locked | Ensure only one instance of the backend is running, and close any DB viewers |
