from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import expenses, summary

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mini Spend Tracker",
    description="Log expenses and view a simple spend summary.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(expenses.router)
app.include_router(summary.router)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def ui():
    index = FRONTEND_DIR / "index.html"
    if not index.exists():
        return {"message": "Spend Tracker API. See /docs."}
    return FileResponse(index)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
