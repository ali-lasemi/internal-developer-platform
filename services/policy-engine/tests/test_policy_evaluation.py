from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_policy_allows_valid_service():
    response = client.post(
        "/policies/evaluate",
        json={
            "service_name": "payments-api",
            "owner": "payments-team",
            "repository": "https://github.com/example/payments-api",
            "description": "Payments API service",
            "environment": "development"
        }
    )

    assert response.status_code == 200

    result = response.json()

    assert result["decision"] == "allowed"
    assert result["violations"] == []


def test_policy_denies_invalid_service_name():
    response = client.post(
        "/policies/evaluate",
        json={
            "service_name": "Payments_API",
            "owner": "payments-team",
            "repository": "https://github.com/example/payments-api",
            "description": "Payments API service",
            "environment": "development"
        }
    )

    assert response.status_code == 200

    result = response.json()

    assert result["decision"] == "denied"

    rules = {
        violation["rule"]
        for violation in result["violations"]
    }

    assert "service-name-format" in rules


def test_policy_denies_external_repository():
    response = client.post(
        "/policies/evaluate",
        json={
            "service_name": "payments-api",
            "owner": "payments-team",
            "repository": "https://gitlab.com/example/payments-api",
            "description": "Payments API service",
            "environment": "development"
        }
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "denied"


def test_policy_denies_unknown_environment():
    response = client.post(
        "/policies/evaluate",
        json={
            "service_name": "payments-api",
            "owner": "payments-team",
            "repository": "https://github.com/example/payments-api",
            "description": "Payments API service",
            "environment": "qa"
        }
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "denied"
