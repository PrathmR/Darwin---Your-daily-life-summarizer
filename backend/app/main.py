# backend/app/main.py
# -----------------------Claude code below-------------------------------------------------------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import auth as auth_router
from app.api.routes import meet_summary
from app.api.routes import websockets
from app.api.routes import live_record
from app.models.user import Base
from app.models.summary import Summary  # ensure loaded
from app.models.task import Task  # ensure loaded
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

    # 📡 WEBSOCKETS
    app.include_router(websockets.router)
    app.include_router(live_record.router)

    return app

app = create_app()
Base.metadata.create_all(bind=engine)










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
