from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.database import engine, Base
from app.routers import expenses, summary

# Recreate tables to ensure user_id column exists
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spend Tracker API")

app.include_router(expenses.router)
app.include_router(summary.router)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Spend Tracker API is running. Go to /docs for API documentation."}
