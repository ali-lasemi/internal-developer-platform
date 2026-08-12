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

    tokens = login.json()

    assert tokens["access_token"]
    assert tokens["refresh_token"]

    return tokens


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

    assert rotated["access_token"]
    assert rotated["refresh_token"]

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

    refresh = httpx.post(
        f"{IDENTITY_API}/auth/refresh",
        json={
            "refresh_token": tokens[
                "refresh_token"
            ]
        },
        timeout=10.0
    )

    assert refresh.status_code == 401


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

    assert result["service"] == service_name
    assert result["policy"] == "allowed"
    assert result["catalog"] == "registered"
    assert result["workflow"] == "started"
    assert result["status"] == "provisioning"

    catalog_response = httpx.get(
        f"{CATALOG_API}/catalog",
        timeout=10.0
    )

    assert catalog_response.status_code == 200

    catalog = catalog_response.json()

    matching_services = [
        service
        for service in catalog
        if service["name"] == service_name
    ]

    assert len(
        matching_services
    ) == 1

    events_response = httpx.get(
        f"{EVENT_API}/events",
        timeout=10.0
    )

    assert events_response.status_code == 200

    events = events_response.json()

    event_types = {
        event["type"]
        for event in events
        if event["subject"] == service_name
    }

    assert "service.created" in event_types
    assert "service.provisioning.started" in event_types


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

    rules = {
        violation["rule"]
        for violation in result["violations"]
    }

    assert "service-name-format" in rules
    assert "repository-source" in rules

    catalog_response = httpx.get(
        f"{CATALOG_API}/catalog",
        timeout=10.0
    )

    assert catalog_response.status_code == 200

    catalog = catalog_response.json()

    matching_services = [
        service
        for service in catalog
        if service["name"] == service_name
    ]

    assert matching_services == []

    events_response = httpx.get(
        f"{EVENT_API}/events",
        timeout=10.0
    )

    assert events_response.status_code == 200

    events = events_response.json()

    policy_events = [
        event
        for event in events
        if (
            event["subject"] == service_name
            and event["type"] == "policy.evaluated"
        )
    ]

    assert len(policy_events) >= 1

    latest = policy_events[-1]

    assert latest["data"]["decision"] == "denied"