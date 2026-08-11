from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_catalog_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_service():
    response = client.post(
        "/catalog",
        json={
            "name": "example-service",
            "owner": "platform-team",
            "repository": "github/example",
            "description": "Example application"
        }
    )

    assert response.status_code == 200
