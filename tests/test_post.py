"""Integration tests for the POST endpoints."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

# Larger than any id in the test database, but still a valid integer column.
MISSING_ID = 2_000_000_000


def test_create_game(client: TestClient) -> None:
    body = {"title": "  New Game  ", "genre": "Puzzle", "release_date": "2024-05-01"}

    response = client.post("/games", json=body)

    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "New Game"
    assert created["genre"] == "Puzzle"
    assert created["release_date"] == "2024-05-01"
    assert created["version"] == 0
    assert response.headers["Location"] == f"/games/{created['id']}"
    assert response.headers["ETag"] == '"0"'
    assert client.get(response.headers["Location"]).json() == created


@pytest.mark.parametrize(
    "body",
    [
        {"genre": "Puzzle"},
        {"title": "   ", "genre": "Puzzle"},
        {"title": "x" * 201, "genre": "Puzzle"},
        {"title": "New Game", "genre": "Puzzle", "release_date": "not a date"},
        {"title": "New Game", "genre": "Puzzle", "id": 1},
        {"title": "New Game", "genre": "Puzzle", "version": 5},
    ],
    ids=["missing-title", "blank-title", "long-title", "bad-date", "id", "version"],
)
def test_create_game_with_invalid_data_returns_422(
    client: TestClient, body: dict[str, Any]
) -> None:
    response = client.post("/games", json=body)

    assert response.status_code == 422


def test_create_review(client: TestClient, game: dict[str, Any]) -> None:
    url = f"/games/{game['id']}/reviews"

    response = client.post(url, json={"rating": 4, "comment": "Nice"})

    assert response.status_code == 201
    review = response.json()
    assert review["rating"] == 4
    assert review["comment"] == "Nice"
    assert client.get(url).json() == [review]
    # Reviews do not change the game or its ETag.
    assert client.get(f"/games/{game['id']}").json() == game


@pytest.mark.parametrize(
    "body",
    [{"rating": 0}, {"rating": 6}, {"comment": "No rating"}, {"rating": 3, "x": 1}],
    ids=["rating-too-low", "rating-too-high", "missing-rating", "unknown-field"],
)
def test_create_review_with_invalid_data_returns_422(
    client: TestClient, game: dict[str, Any], body: dict[str, Any]
) -> None:
    response = client.post(f"/games/{game['id']}/reviews", json=body)

    assert response.status_code == 422


def test_create_review_for_missing_game_returns_404(client: TestClient) -> None:
    response = client.post(f"/games/{MISSING_ID}/reviews", json={"rating": 5})

    assert response.status_code == 404


def test_create_game_details(client: TestClient, game: dict[str, Any]) -> None:
    url = f"/games/{game['id']}/details"
    body = {"description": "A test game.", "developer": "Dev", "publisher": "Pub"}

    response = client.post(url, json=body)

    assert response.status_code == 201
    assert response.json() == body
    assert response.headers["Location"] == url
    assert client.get(url).json() == body


def test_create_game_details_twice_returns_409(
    client: TestClient, game: dict[str, Any]
) -> None:
    url = f"/games/{game['id']}/details"
    assert client.post(url, json={"developer": "Dev"}).status_code == 201

    response = client.post(url, json={"developer": "Other"})

    assert response.status_code == 409
    assert client.get(url).json()["developer"] == "Dev"


@pytest.mark.parametrize(
    "body",
    [{}, {"developer": "   "}, {"developer": "x" * 101}, {"developer": "D", "x": 1}],
    ids=["empty", "blank-developer", "long-developer", "unknown-field"],
)
def test_create_game_details_with_invalid_data_returns_422(
    client: TestClient, game: dict[str, Any], body: dict[str, Any]
) -> None:
    response = client.post(f"/games/{game['id']}/details", json=body)

    assert response.status_code == 422


def test_create_game_details_for_missing_game_returns_404(client: TestClient) -> None:
    response = client.post(f"/games/{MISSING_ID}/details", json={"developer": "Dev"})

    assert response.status_code == 404
