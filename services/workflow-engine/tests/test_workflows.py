from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_workflow_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_workflow():
    response = client.post(
        "/workflows",
        json={
            "name": "service-creation",
            "description": "Create new service workflow"
        }
    )

    assert response.status_code == 200


def test_execute_workflow():
    response = client.post(
        "/workflows/service-creation/execute"
    )

    assert response.status_code == 200
