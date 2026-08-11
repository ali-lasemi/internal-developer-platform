from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_template_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_template():
    response = client.post(
        "/templates",
        json={
            "name": "backend-service",
            "description": "Backend golden path",
            "version": "1.0",
            "type": "service"
        }
    )

    assert response.status_code == 200
