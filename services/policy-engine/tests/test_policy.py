from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_policy_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_policy():
    response = client.post(
        "/policies",
        json={
            "name": "service-policy",
            "description": "Validate service requirements",
            "category": "security"
        }
    )

    assert response.status_code == 200


def test_policy_evaluation():
    response = client.post("/policies/evaluate")

    assert response.json()["decision"] == "allowed"
