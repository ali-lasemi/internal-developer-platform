import os

os.environ["DATABASE_URL"] = "sqlite:///./test_identity.db"
os.environ["JWT_SECRET"] = "test-secret"

from fastapi.testclient import TestClient

from app.db.database import Base
from app.db.database import engine
from app.main import app


Base.metadata.drop_all(
    bind=engine
)

Base.metadata.create_all(
    bind=engine
)

client = TestClient(app)


def test_identity_health():
    response = client.get(
        "/health"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login():
    registration = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "strong-password",
            "team": "platform-team",
            "role": "developer"
        }
    )

    assert registration.status_code == 201
    assert registration.json()["username"] == "alice"
    assert registration.json()["active"] is True

    login = client.post(
        "/auth/token",
        json={
            "username": "alice",
            "password": "strong-password"
        }
    )

    assert login.status_code == 200
    assert login.json()["access_token"]
    assert login.json()["token_type"] == "bearer"


def test_duplicate_user_is_rejected():
    response = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "other@example.com",
            "password": "strong-password",
            "team": "platform-team",
            "role": "developer"
        }
    )

    assert response.status_code == 409


def test_invalid_login():
    response = client.post(
        "/auth/token",
        json={
            "username": "missing-user",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 401
