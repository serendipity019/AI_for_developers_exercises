"""
FastAPI Application — Main Entry Point

Includes:
- All routers (auth, missions, heroes)
- Custom timing middleware
- Database initialization
- CORS (if needed)

Run:  uvicorn app.main:app --reload
Docs: http://127.0.0.1:8000/docs
"""
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import get_settings
from app.db import create_db_and_tables
from app.routers import auth_router, heroes_router, missions_router

settings = get_settings()

# --- Lifespan and Database---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables. Shutdown: cleanup."""
    create_db_and_tables()
    print("Database ready [OK]")
    yield
    print("Shutting down...")

app = FastAPI(
    title="Secure Hero Missions API",
    description="API for managing heroes and missions with JWT authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Middleware ---

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom timing middleware
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.4f}"
        response.headers["X-Request-ID"] = request_id
        return response


app.add_middleware(TimingMiddleware)

# ------- Routers ---------
app.include_router(auth_router)
app.include_router(heroes_router)
app.include_router(missions_router)

@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Hero Missions API", "status": "running"}