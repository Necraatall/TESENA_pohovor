from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app.api.deps import get_db
from app.main import app


def test_liveness_does_not_depend_on_database(
    client: TestClient,
) -> None:
    def unavailable_database() -> None:
        raise SQLAlchemyError("Simulated database failure")

    app.dependency_overrides[get_db] = unavailable_database

    try:
        response = client.get("/health/live")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_reports_available_database(
    client: TestClient,
) -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_reports_unavailable_database(
    client: TestClient,
) -> None:
    unavailable_session = MagicMock(spec=Session)
    unavailable_session.execute.side_effect = SQLAlchemyError(
        "Simulated database failure"
    )
    app.dependency_overrides[get_db] = lambda: unavailable_session

    try:
        response = client.get("/health/ready")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
