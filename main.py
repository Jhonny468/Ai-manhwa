from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.config import settings
from app.api.routes import router
from app.db.base import Base
from app.db.session import engine
from app.models import entities  # noqa: F401

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
Base.metadata.create_all(bind=engine)  # MVP convenience; use Alembic migrations for production.
app.include_router(router, prefix="/api/v1")
STATIC_DIR = Path(__file__).parent / "static"

@app.get("/", include_in_schema=False)
def mobile_app():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}

app.mount("/", StaticFiles(directory=STATIC_DIR), name="static")
