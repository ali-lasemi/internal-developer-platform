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

EVENT_API = os.getenv(
    "EVENT_API_URL",
    "http://localhost:8007"
)


def test_complete_service_provisioning_journey():
    suffix = uuid.uuid4().hex[:8]

    service_name = f"payments-api-{suffix}"

    response = httpx.post(
        f"{PLATFORM_API}/api/v1/provision/services",
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

    assert len(matching_services) == 1
    assert matching_services[0]["owner"] == "payments-team"

    events_response = httpx.get(
        f"{EVENT_API}/events",
        timeout=10.0
    )

    assert events_response.status_code == 200

    events = events_response.json()

    service_events = [
        event
        for event in events
        if event["subject"] == service_name
    ]

    event_types = {
        event["type"]
        for event in service_events
    }

    assert "service.created" in event_types
    assert "service.provisioning.started" in event_types
