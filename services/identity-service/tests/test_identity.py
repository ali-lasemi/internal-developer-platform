from fastapi.testclient import TestClient

from app.main import app


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


def test_invalid_login():
    response = client.post(
        "/auth/token",
        json={
            "username": "missing-user",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 401
