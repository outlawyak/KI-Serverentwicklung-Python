"""Pydantic response models for the REST API.

`from_attributes=True` lets FastAPI build them directly from the SQLAlchemy
models in `app.models`.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


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
    details: GameDetailsResponse | None
    reviews: list[ReviewResponse]
