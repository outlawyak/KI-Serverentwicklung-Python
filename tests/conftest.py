"""Fixtures for integration tests against the real database.

Each test runs inside a transaction that is rolled back afterwards, so the
tests leave the database unchanged. The app's `session.commit()` only
releases a savepoint inside that transaction.
"""

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import engine, get_session
from app.main import app


@pytest.fixture
def session() -> Iterator[Session]:
    with engine.connect() as connection:
        transaction = connection.begin()
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield session
        finally:
            session.close()
            transaction.rollback()


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = lambda: session
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def game(client: TestClient) -> dict[str, Any]:
    """A game created through the API, so tests do not rely on seed data."""
    body = {"title": "Pytest Quest", "genre": "PytestGenre", "release_date": None}
    response = client.post("/games", json=body)
    assert response.status_code == 201
    return response.json()
