"""Pydantic request and response models for the REST API.

`from_attributes=True` lets FastAPI build the response models directly from
the SQLAlchemy models in `app.models`.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class GameDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    description: str | None
    developer: str | None
    publisher: str | None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rating: int
    comment: str | None
    created_at: datetime


class GameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    genre: str
    release_date: date | None
    # Exposed so clients can send it back for lost-update protection (T3.6).
    version: int
    # Details and reviews are served separately (GET /games/{id}/details and
    # /games/{id}/reviews), so changing them does not change the game's ETag.


class GameCreate(BaseModel):
    # Unknown fields such as `id` or `version` are rejected instead of being
    # silently ignored; leading and trailing whitespace is stripped, so a
    # blank title fails min_length.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    # Lengths match the varchar columns in `db/schema.sql`.
    title: str = Field(min_length=1, max_length=200)
    genre: str = Field(min_length=1, max_length=50)
    release_date: date | None = None


class ReviewCreate(BaseModel):
    # Same rules as GameCreate: unknown fields are rejected, whitespace is
    # stripped.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    # Range matches the CHECK constraint in `db/schema.sql`.
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
