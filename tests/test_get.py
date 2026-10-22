"""Integration tests for the GET endpoints."""

from typing import Any

from fastapi.testclient import TestClient

# Larger than any id in the test database, but still a valid integer column.
MISSING_ID = 2_000_000_000


def test_get_game(client: TestClient, game: dict[str, Any]) -> None:
    response = client.get(f"/games/{game['id']}")

    assert response.status_code == 200
    assert response.json() == game
    assert response.headers["ETag"] == f'"{game["version"]}"'


def test_get_missing_game_returns_404(client: TestClient) -> None:
    response = client.get(f"/games/{MISSING_ID}")

    assert response.status_code == 404


def test_conditional_get_with_matching_etag_returns_304(
    client: TestClient, game: dict[str, Any]
) -> None:
    etag = client.get(f"/games/{game['id']}").headers["ETag"]

    response = client.get(f"/games/{game['id']}", headers={"If-None-Match": etag})

    assert response.status_code == 304
    assert response.content == b""
    assert response.headers["ETag"] == etag


def test_conditional_get_with_other_etag_returns_200(
    client: TestClient, game: dict[str, Any]
) -> None:
    response = client.get(f"/games/{game['id']}", headers={"If-None-Match": '"999"'})

    assert response.status_code == 200
    assert response.json() == game


def test_search_by_title_matches_part_ignoring_case(
    client: TestClient, game: dict[str, Any]
) -> None:
    response = client.get("/games", params={"title": "pytest q"})

    assert response.status_code == 200
    assert response.json() == [game]


def test_search_by_genre_matches_whole_genre_ignoring_case(
    client: TestClient, game: dict[str, Any]
) -> None:
    assert client.get("/games", params={"genre": "pytestgenre"}).json() == [game]
    assert client.get("/games", params={"genre": "Pytest"}).json() == []


def test_search_by_title_and_genre(client: TestClient, game: dict[str, Any]) -> None:
    params = {"title": "Pytest Quest", "genre": "PytestGenre"}
    assert client.get("/games", params=params).json() == [game]

    params = {"title": "Pytest Quest", "genre": "Other"}
    assert client.get("/games", params=params).json() == []


def test_search_treats_wildcards_literally(
    client: TestClient, game: dict[str, Any]
) -> None:
    response = client.get("/games", params={"title": "Pytest%"})

    assert response.status_code == 200
    assert game not in response.json()
