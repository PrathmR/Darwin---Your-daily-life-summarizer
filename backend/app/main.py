# backend/app/main.py
# -----------------------Claude code below-------------------------------------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import auth as auth_router
from app.api.routes import meet_summary
from app.api.routes import websockets
from app.api.routes import live_record
from app.api.routes import teams as teams_router
from app.models.user import Base
from app.models.summary import Summary  # ensure loaded
from app.models.task import Task  # ensure loaded
from app.models.team_member import TeamMember  # ensure loaded
from app.db.session import engine

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

    # ✅ FIXED: Properly handle CORS origins
    # The settings.BACKEND_CORS_ORIGINS is already parsed as a list by Pydantic
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,  # This is now a list
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # 🔐 AUTH MUST HAVE NO PREFIX CHANGE
    app.include_router(auth_router.router)

    # 🧠 API ROUTES CAN HAVE PREFIX
    app.include_router(meet_summary.router, prefix="/api")
    app.include_router(teams_router.router, prefix="/api")

    # 📡 WEBSOCKETS
    app.include_router(websockets.router)
    app.include_router(live_record.router)

    return app

app = create_app()
Base.metadata.create_all(bind=engine)

# Auto-migrate: add any missing columns to existing tables
import sqlite3 as _sqlite3
with engine.connect() as _conn:
    _raw = _conn.connection.dbapi_connection
    _cur = _raw.cursor()
    
    # summaries.screenshots
    _cur.execute("PRAGMA table_info(summaries)")
    _existing_cols = {row[1] for row in _cur.fetchall()}
    if "screenshots" not in _existing_cols:
        _cur.execute("ALTER TABLE summaries ADD COLUMN screenshots JSON")
        _raw.commit()
        print("✅ Auto-migrated: added 'screenshots' column to summaries table")
    
    # users.meeting_role
    _cur.execute("PRAGMA table_info(users)")
    _user_cols = {row[1] for row in _cur.fetchall()}
    if "meeting_role" not in _user_cols:
        _cur.execute("ALTER TABLE users ADD COLUMN meeting_role TEXT DEFAULT 'general'")
        _raw.commit()
        print("✅ Auto-migrated: added 'meeting_role' column to users table")










# -----------------------------------------------------------------------







# # backend/app/main.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.core.config import settings
# from app.api.routes import auth as auth_router
# from app.api.routes import meet_summary
# from app.models.user import Base
# from app.db.session import engine

# def create_app() -> FastAPI:
#     app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[
#             settings.FRONTEND_URL,   # e.g. http://localhost:5173
#         ],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

#     # 🔐 AUTH MUST HAVE NO PREFIX CHANGE
#     app.include_router(auth_router.router)

#     # 🧠 API ROUTES CAN HAVE PREFIX
#     app.include_router(meet_summary.router, prefix="/api")

#     return app

# app = create_app()
# Base.metadata.create_all(bind=engine)








# -----------not working code below-------------------------------------------------------


# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.core.config import settings
# from app.api.routes import auth as auth_router
# from app.api.routes import meet_summary
# from app.models.user import Base
# from app.db.session import engine

# def create_app() -> FastAPI:
#     app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[settings.FRONTEND_URL],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

#     # AUTH — UNTOUCHED
#     app.include_router(auth_router.router)

#     # MEET SUMMARY
#     app.include_router(meet_summary.router, prefix="/api")

#     return app

# app = create_app()
# Base.metadata.create_all(bind=engine)







# -------------------------------------------------------------------------------






# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.core.config import settings
# from app.api.routes import auth as auth_router
# from app.api.routes import meet_summary
# from app.models.user import Base
# from app.db.session import engine

# def create_app() -> FastAPI:
#     app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[settings.FRONTEND_URL],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

#     # Auth untouched
#     app.include_router(auth_router.router)

#     # Meet summary API
#     app.include_router(meet_summary.router, prefix="/api")

#     return app

# app = create_app()
# Base.metadata.create_all(bind=engine)









# # ---------ChatGPT changed code 1 below-----------------------------------------------------


# # # app/main.py
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.core.config import settings
# from app.api.routes import auth as auth_router
# from app.api.routes import meet_summary
# from app.models.user import Base
# from app.db.session import engine


# def create_app() -> FastAPI:
#     app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

#     origins = settings.BACKEND_CORS_ORIGINS or [
#         settings.FRONTEND_URL
#     ]
#     origins = [o for o in origins if o]

#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=origins,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

#     # ✅ KEEP AUTH ROUTES UNCHANGED (CRITICAL)
#     app.include_router(auth_router.router)

#     # ✅ NEW FEATURES USE /api PREFIX
#     app.include_router(meet_summary.router, prefix="/api")

#     @app.get("/health")
#     def health_check():
#         return {"status": "ok"}

#     return app


# app = create_app()

# # Dev-only
# Base.metadata.create_all(bind=engine)










# --------------------------original code below-----------------------------------------------------





# # app/main.py

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.core.config import settings
# from app.api.routes import auth as auth_router
# from app.models.user import Base
# from app.db.session import engine


# def create_app() -> FastAPI:
#     app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

#     origins = settings.BACKEND_CORS_ORIGINS or [
#         settings.FRONTEND_URL
#     ]

#     origins = [o for o in origins if o]

#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=origins,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

#     app.include_router(auth_router.router)

#     @app.get("/health")
#     def health_check():
#         return {"status": "ok"}

#     return app


# app = create_app()

# # Dev-only: create tables
# Base.metadata.create_all(bind=engine)
