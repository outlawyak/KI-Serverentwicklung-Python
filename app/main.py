"""FastAPI application entry point.

Run locally: `uv run uvicorn app.main:app --reload`
"""

from fastapi import FastAPI, HTTPException, status
from sqlalchemy import func, select, text
from sqlalchemy.orm import joinedload, selectinload

from app.database import SessionDep
from app.models import Game
from app.schemas import GameResponse

app = FastAPI(title="Games API")


@app.get("/health")
def health(session: SessionDep) -> dict[str, str]:
    """Check that the app can open a DB session and run a query."""
    session.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/games", response_model=list[GameResponse])
def search_games(
    session: SessionDep, title: str | None = None, genre: str | None = None
) -> list[Game]:
    """Return all games, optionally filtered by title and/or genre.

    `title` matches any part of the title, `genre` the whole genre; both
    ignore case.
    """
    query = (
        select(Game)
        .options(joinedload(Game.details), selectinload(Game.reviews))
        .order_by(Game.id)
    )
    if title is not None:
        # autoescape treats % and _ in the input as literal characters.
        query = query.where(Game.title.icontains(title, autoescape=True))
    if genre is not None:
        query = query.where(func.lower(Game.genre) == genre.lower())
    return list(session.scalars(query))


@app.get("/games/{game_id}", response_model=GameResponse)
def get_game(game_id: int, session: SessionDep) -> Game:
    """Return a single game incl. details and reviews, 404 if it does not exist."""
    # Load the related objects up front instead of lazily during serialization.
    game = session.get(
        Game,
        game_id,
        options=[joinedload(Game.details), selectinload(Game.reviews)],
    )
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Game not found")
    return game
