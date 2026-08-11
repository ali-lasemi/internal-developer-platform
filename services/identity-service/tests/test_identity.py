from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_identity_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_identity():
    response = client.post(
        "/identities",
        json={
            "username": "developer",
            "email": "developer@example.com",
            "team": "platform-team"
        }
    )

    assert response.status_code == 200
