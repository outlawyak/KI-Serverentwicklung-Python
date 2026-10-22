"""Integration tests for the PUT endpoint."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import set_committed_value

from app.models import Game

# Larger than any id in the test database, but still a valid integer column.
MISSING_ID = 2_000_000_000


def test_update_game(client: TestClient, game: dict[str, Any]) -> None:
    url = f"/games/{game['id']}"
    etag = client.get(url).headers["ETag"]
    body = {"title": "  New Title  ", "genre": "Puzzle", "release_date": "2024-05-01"}

    response = client.put(url, json=body, headers={"If-Match": etag})

    assert response.status_code == 200
    updated = response.json()
    assert updated == {
        "id": game["id"],
        "title": "New Title",
        "genre": "Puzzle",
        "release_date": "2024-05-01",
        "version": game["version"] + 1,
    }
    assert response.headers["ETag"] == f'"{updated["version"]}"'
    assert client.get(url).json() == updated


def test_update_game_with_outdated_etag_returns_412(
    client: TestClient, game: dict[str, Any]
) -> None:
    url = f"/games/{game['id']}"
    etag = client.get(url).headers["ETag"]
    first = {"title": "First", "genre": "Puzzle", "release_date": None}
    assert client.put(url, json=first, headers={"If-Match": etag}).status_code == 200

    # A second client still sends the ETag it read before the first update.
    second = {"title": "Second", "genre": "Puzzle", "release_date": None}
    response = client.put(url, json=second, headers={"If-Match": etag})

    assert response.status_code == 412
    assert client.get(url).json()["title"] == "First"


def test_update_game_changed_after_if_match_check_returns_412(
    client: TestClient, session: Session, game: dict[str, Any]
) -> None:
    url = f"/games/{game['id']}"
    # Another request updates the game and commits.
    other = "UPDATE game SET title = 'Other', version = version + 1 WHERE id = :id"
    session.execute(text(other), {"id": game["id"]})
    session.commit()
    # The app's session still holds the version from before that update, so the
    # If-Match check passes and only the version in the UPDATE's WHERE clause
    # detects the conflict. The session only keeps a weak reference, so `stale`
    # keeps the object alive until the PUT.
    stale = session.get(Game, game["id"])
    set_committed_value(stale, "version", 0)
    body = {"title": "Lost", "genre": "Puzzle", "release_date": None}

    response = client.put(url, json=body, headers={"If-Match": '"0"'})

    assert response.status_code == 412
    assert client.get(url).json()["title"] == "Other"


def test_update_game_without_if_match_returns_428(
    client: TestClient, game: dict[str, Any]
) -> None:
    url = f"/games/{game['id']}"
    body = {"title": "New Title", "genre": "Puzzle", "release_date": None}

    response = client.put(url, json=body)

    assert response.status_code == 428
    assert client.get(url).json() == game


@pytest.mark.parametrize(
    "body",
    [
        {"genre": "Puzzle", "release_date": None},
        {"title": "   ", "genre": "Puzzle", "release_date": None},
        {"title": "x" * 201, "genre": "Puzzle", "release_date": None},
        {"title": "New Title", "genre": "Puzzle"},
        {"title": "New Title", "genre": "Puzzle", "release_date": "not a date"},
        {"title": "New Title", "genre": "Puzzle", "release_date": None, "version": 5},
    ],
    ids=[
        "missing-title",
        "blank-title",
        "long-title",
        "missing-release-date",
        "bad-date",
        "version",
    ],
)
def test_update_game_with_invalid_data_returns_422(
    client: TestClient, game: dict[str, Any], body: dict[str, Any]
) -> None:
    url = f"/games/{game['id']}"

    response = client.put(url, json=body, headers={"If-Match": '"0"'})

    assert response.status_code == 422
    assert client.get(url).json() == game


def test_update_missing_game_returns_404(client: TestClient) -> None:
    body = {"title": "New Title", "genre": "Puzzle", "release_date": None}

    response = client.put(
        f"/games/{MISSING_ID}", json=body, headers={"If-Match": '"0"'}
    )

    assert response.status_code == 404
