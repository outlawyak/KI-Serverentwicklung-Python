"""FastAPI application entry point.

Run locally: `uv run uvicorn app.main:app --reload`
"""

from fastapi import FastAPI
from sqlalchemy import text

from app.database import SessionDep

app = FastAPI(title="Games API")


@app.get("/health")
def health(session: SessionDep) -> dict[str, str]:
    """Check that the app can open a DB session and run a query."""
    session.execute(text("SELECT 1"))
    return {"status": "ok"}
