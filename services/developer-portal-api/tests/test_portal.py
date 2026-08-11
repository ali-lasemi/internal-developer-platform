from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_portal_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_services_endpoint():
    response = client.get("/portal/services")

    assert response.status_code == 200
    assert "platform-api" in response.json()["services"]


def test_portal_action():
    response = client.post(
        "/portal/actions",
        json={
            "service": "backend-service",
            "action": "create",
            "user": "developer"
        }
    )

    assert response.status_code == 200
