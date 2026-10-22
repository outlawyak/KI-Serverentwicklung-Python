"""SQLAlchemy engine and the session dependency for FastAPI."""

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings

# create_engine does not connect yet; connections are opened on first use.
engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


def get_session() -> Iterator[Session]:
    """Open one session per request and close it afterwards."""
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
