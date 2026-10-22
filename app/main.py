"""FastAPI application entry point.

Run locally: `uv run uvicorn app.main:app --reload`
"""

from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Response, status
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from app.database import SessionDep
from app.models import Game, GameDetails, Review
from app.schemas import (
    GameCreate,
    GameDetailsCreate,
    GameDetailsResponse,
    GameResponse,
    ReviewCreate,
    ReviewResponse,
)

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
    query = select(Game).order_by(Game.id)
    if title is not None:
        # autoescape treats % and _ in the input as literal characters.
        query = query.where(Game.title.icontains(title, autoescape=True))
    if genre is not None:
        query = query.where(func.lower(Game.genre) == genre.lower())
    return list(session.scalars(query))


@app.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(
    body: GameCreate, session: SessionDep, response: Response
) -> GameResponse:
    """Create a game from a validated body; invalid data is rejected with 422.

    The response carries the new game's URL in Location and its ETag, so a
    client can use it right away for conditional requests.
    """
    game = Game(**body.model_dump())
    session.add(game)
    session.commit()
    response.headers["Location"] = f"/games/{game.id}"
    response.headers["ETag"] = make_etag(game)
    return GameResponse.model_validate(game)


def make_etag(game: Game) -> str:
    """Strong ETag from the game's version, which changes on every UPDATE.

    Details and reviews are not part of the game response, so they do not
    affect it.
    """
    return f'"{game.version}"'


def etag_matches(if_none_match: str, etag: str) -> bool:
    """Weak comparison as required for If-None-Match (RFC 9110, 13.1.2)."""
    if if_none_match.strip() == "*":
        return True
    candidates = (tag.strip().removeprefix("W/") for tag in if_none_match.split(","))
    return etag in candidates


@app.get(
    "/games/{game_id}",
    response_model=GameResponse,
    responses={status.HTTP_304_NOT_MODIFIED: {"description": "Not Modified"}},
)
def get_game(
    game_id: int,
    session: SessionDep,
    response: Response,
    if_none_match: Annotated[str | None, Header()] = None,
) -> GameResponse | Response:
    """Return a single game, 404 if it does not exist.

    Supports conditional GET: the response carries an ETag, and a request whose
    If-None-Match contains that ETag gets 304 Not Modified without a body.
    """
    game = session.get(Game, game_id)
    if game is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Game not found")

    etag = make_etag(game)
    if if_none_match is not None and etag_matches(if_none_match, etag):
        return Response(
            status_code=status.HTTP_304_NOT_MODIFIED, headers={"ETag": etag}
        )
    response.headers["ETag"] = etag
    return GameResponse.model_validate(game)


@app.get("/games/{game_id}/details", response_model=GameDetailsResponse)
def get_game_details(game_id: int, session: SessionDep) -> GameDetails:
    """Return the details of a game, 404 if the game or its details do not exist."""
    if session.get(Game, game_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Game not found")
    query = select(GameDetails).where(GameDetails.game_id == game_id)
    details = session.scalars(query).one_or_none()
    if details is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Game details not found")
    return details


@app.post(
    "/games/{game_id}/details",
    response_model=GameDetailsResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_game_details(
    game_id: int, body: GameDetailsCreate, session: SessionDep, response: Response
) -> GameDetails:
    """Create the details of a game, 404 if the game does not exist.

    A game has at most one details record, so a second POST is rejected with
    409. Invalid data is rejected with 422.
    """
    already_exists = HTTPException(
        status.HTTP_409_CONFLICT, detail="Game details already exist"
    )
    if session.get(Game, game_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Game not found")
    query = select(GameDetails.id).where(GameDetails.game_id == game_id)
    if session.scalars(query).first() is not None:
        raise already_exists
    details = GameDetails(game_id=game_id, **body.model_dump())
    session.add(details)
    try:
        session.commit()
    except IntegrityError:
        # A concurrent request created the details between the check above
        # and this commit; the unique constraint on game_id rejected ours.
        session.rollback()
        raise already_exists from None
    response.headers["Location"] = f"/games/{game_id}/details"
    return details


@app.get("/games/{game_id}/reviews", response_model=list[ReviewResponse])
def get_game_reviews(game_id: int, session: SessionDep) -> list[Review]:
    """Return all reviews of a game, 404 if the game does not exist."""
    if session.get(Game, game_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Game not found")
    query = select(Review).where(Review.game_id == game_id).order_by(Review.id)
    return list(session.scalars(query))


@app.post(
    "/games/{game_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review(game_id: int, body: ReviewCreate, session: SessionDep) -> Review:
    """Add a review to a game, 404 if the game does not exist.

    Invalid data is rejected with 422. Reviews are not part of the game
    response, so the game's version and ETag stay the same.
    """
    if session.get(Game, game_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Game not found")
    review = Review(game_id=game_id, **body.model_dump())
    session.add(review)
    session.commit()
    return review
