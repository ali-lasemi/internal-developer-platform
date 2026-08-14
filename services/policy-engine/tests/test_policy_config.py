from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_policy_document_is_exposed():
    response = client.get(
        "/policies"
    )

    assert response.status_code == 200

    policy = response.json()

    assert policy["name"] == "default-service-policy"
    assert policy["enabled"] is True
    assert "rules" in policy


def test_policy_reload():
    response = client.post(
        "/policies/reload"
    )

    assert response.status_code == 200
    assert (
        response.json()["name"]
        == "default-service-policy"
    )


def test_policy_allows_valid_service():
    response = client.post(
        "/policies/evaluate",
        json={
            "service_name": "payments-api",
            "owner": "payments-team",
            "repository": (
                "https://github.com/example/"
                "payments-api"
            ),
            "description": "Payments API service",
            "environment": "development"
        }
    )

    assert response.status_code == 200
    assert (
        response.json()["decision"]
        == "allowed"
    )


def test_policy_denies_non_github_repository():
    response = client.post(
        "/policies/evaluate",
        json={
            "service_name": "payments-api",
            "owner": "payments-team",
            "repository": (
                "https://gitlab.com/example/"
                "payments-api"
            ),
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

    assert "repository-source" in rules
