import os
import uuid

import httpx


PLATFORM_API = os.getenv(
    "PLATFORM_API_URL",
    "http://localhost:8000"
)

CATALOG_API = os.getenv(
    "CATALOG_API_URL",
    "http://localhost:8001"
)

IDENTITY_API = os.getenv(
    "IDENTITY_API_URL",
    "http://localhost:8005"
)

EVENT_API = os.getenv(
    "EVENT_API_URL",
    "http://localhost:8007"
)


def create_authenticated_session():
    suffix = uuid.uuid4().hex[:8]

    username = f"developer-{suffix}"

    registration = httpx.post(
        f"{IDENTITY_API}/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "integration-password",
            "team": "payments-team",
            "role": "developer"
        },
        timeout=10.0
    )

    assert registration.status_code == 201

    login = httpx.post(
        f"{IDENTITY_API}/auth/token",
        json={
            "username": username,
            "password": "integration-password"
        },
        timeout=10.0
    )

    assert login.status_code == 200

    return login.json()


def test_refresh_token_rotation():
    tokens = create_authenticated_session()

    refresh = httpx.post(
        f"{IDENTITY_API}/auth/refresh",
        json={
            "refresh_token": tokens[
                "refresh_token"
            ]
        },
        timeout=10.0
    )

    assert refresh.status_code == 200

    rotated = refresh.json()

    assert (
        rotated["refresh_token"]
        != tokens["refresh_token"]
    )

    replay = httpx.post(
        f"{IDENTITY_API}/auth/refresh",
        json={
            "refresh_token": tokens[
                "refresh_token"
            ]
        },
        timeout=10.0
    )

    assert replay.status_code == 401


def test_logout_revokes_session():
    tokens = create_authenticated_session()

    logout = httpx.post(
        f"{IDENTITY_API}/auth/logout",
        json={
            "refresh_token": tokens[
                "refresh_token"
            ]
        },
        timeout=10.0
    )

    assert logout.status_code == 204


def test_complete_service_provisioning_journey():
    suffix = uuid.uuid4().hex[:8]

    service_name = f"payments-api-{suffix}"

    tokens = create_authenticated_session()

    response = httpx.post(
        f"{PLATFORM_API}/api/v1/provision/services",
        headers={
            "Authorization": (
                f"Bearer {tokens['access_token']}"
            )
        },
        json={
            "name": service_name,
            "owner": "payments-team",
            "repository": f"https://github.com/example/{service_name}",
            "description": "Integration test managed service",
            "template": "backend-service",
            "environment": "development"
        },
        timeout=20.0
    )

    assert response.status_code == 200

    result = response.json()

    assert result["policy"] == "allowed"
    assert result["catalog"] == "registered"

    catalog_response = httpx.get(
        f"{CATALOG_API}/catalog",
        timeout=10.0
    )

    assert catalog_response.status_code == 200

    service = next(
        item
        for item in catalog_response.json()
        if item["name"] == service_name
    )

    lifecycle = httpx.post(
        f"{CATALOG_API}/catalog/{service['id']}/lifecycle",
        json={
            "lifecycle": "development"
        },
        timeout=10.0
    )

    assert lifecycle.status_code == 200

    transition = lifecycle.json()

    assert transition["previous_lifecycle"] == "created"
    assert transition["lifecycle"] == "development"

    staging = httpx.post(
        f"{CATALOG_API}/catalog/{service['id']}/lifecycle",
        json={
            "lifecycle": "staging"
        },
        timeout=10.0
    )

    assert staging.status_code == 200
    assert staging.json()["lifecycle"] == "staging"

    production = httpx.post(
        f"{CATALOG_API}/catalog/{service['id']}/lifecycle",
        json={
            "lifecycle": "production"
        },
        timeout=10.0
    )

    assert production.status_code == 200
    assert production.json()["lifecycle"] == "production"


def test_invalid_lifecycle_transition_is_rejected():
    suffix = uuid.uuid4().hex[:8]

    service_name = f"lifecycle-api-{suffix}"

    create = httpx.post(
        f"{CATALOG_API}/catalog",
        json={
            "name": service_name,
            "owner": "platform-team",
            "repository": f"https://github.com/example/{service_name}",
            "description": "Lifecycle validation service",
            "lifecycle": "created"
        },
        timeout=10.0
    )

    assert create.status_code == 201

    service_id = create.json()["id"]

    invalid = httpx.post(
        f"{CATALOG_API}/catalog/{service_id}/lifecycle",
        json={
            "lifecycle": "production"
        },
        timeout=10.0
    )

    assert invalid.status_code == 409


def test_denied_service_is_blocked():
    suffix = uuid.uuid4().hex[:8]

    service_name = f"Invalid_Service_{suffix}"

    tokens = create_authenticated_session()

    response = httpx.post(
        f"{PLATFORM_API}/api/v1/provision/services",
        headers={
            "Authorization": (
                f"Bearer {tokens['access_token']}"
            )
        },
        json={
            "name": service_name,
            "owner": "payments-team",
            "repository": (
                "https://gitlab.com/example/"
                f"{service_name}"
            ),
            "description": "Invalid governed service",
            "template": "backend-service",
            "environment": "development"
        },
        timeout=20.0
    )

    assert response.status_code == 200

    result = response.json()

    assert result["policy"] == "denied"
    assert result["catalog"] == "not_registered"
    assert result["workflow"] == "not_started"
    assert result["status"] == "rejected"
