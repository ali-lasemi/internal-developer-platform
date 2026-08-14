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

    assert result["template"] == "backend-service"
    assert result["template_version"] == "1.0.0"
    assert result["template_status"] == "resolved"
    assert result["policy"] == "allowed"
    assert result["catalog"] == "registered"
    assert result["workflow"] == "completed"
    assert result["workflow_execution_id"]
    assert len(result["workflow_steps"]) >= 1
    assert all(
        step["status"] == "completed"
        for step in result["workflow_steps"]
    )

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


def test_lifecycle_change_emits_domain_event():
    suffix = uuid.uuid4().hex[:8]

    service_name = f"events-api-{suffix}"

    create = httpx.post(
        f"{CATALOG_API}/catalog",
        json={
            "name": service_name,
            "owner": "platform-team",
            "repository": f"https://github.com/example/{service_name}",
            "description": "Lifecycle event validation service",
            "lifecycle": "created"
        },
        timeout=10.0
    )

    assert create.status_code == 201

    service_id = create.json()["id"]

    transition = httpx.post(
        f"{CATALOG_API}/catalog/{service_id}/lifecycle",
        json={
            "lifecycle": "development"
        },
        timeout=10.0
    )

    assert transition.status_code == 200

    events_response = httpx.get(
        f"{EVENT_API}/events",
        timeout=10.0
    )

    assert events_response.status_code == 200

    matching = [
        event
        for event in events_response.json()
        if (
            event["type"] == "service.lifecycle.changed"
            and event["subject"] == service_name
        )
    ]

    assert len(matching) >= 1

    latest = matching[-1]

    assert latest["data"]["previous_lifecycle"] == "created"
    assert latest["data"]["lifecycle"] == "development"


def test_lifecycle_history_is_persisted():
    suffix = uuid.uuid4().hex[:8]

    service_name = f"history-api-{suffix}"

    create = httpx.post(
        f"{CATALOG_API}/catalog",
        json={
            "name": service_name,
            "owner": "platform-team",
            "repository": f"https://github.com/example/{service_name}",
            "description": "Lifecycle history test service",
            "lifecycle": "created"
        },
        timeout=10.0
    )

    assert create.status_code == 201

    service_id = create.json()["id"]

    development = httpx.post(
        f"{CATALOG_API}/catalog/{service_id}/lifecycle",
        json={
            "lifecycle": "development"
        },
        timeout=10.0
    )

    assert development.status_code == 200

    staging = httpx.post(
        f"{CATALOG_API}/catalog/{service_id}/lifecycle",
        json={
            "lifecycle": "staging"
        },
        timeout=10.0
    )

    assert staging.status_code == 200

    history_response = httpx.get(
        f"{CATALOG_API}/catalog/{service_id}/lifecycle/history",
        timeout=10.0
    )

    assert history_response.status_code == 200

    history = history_response.json()

    assert len(history) == 2

    assert history[0]["previous_lifecycle"] == "created"
    assert history[0]["lifecycle"] == "development"

    assert history[1]["previous_lifecycle"] == "development"
    assert history[1]["lifecycle"] == "staging"


def test_unknown_template_is_rejected():
    suffix = uuid.uuid4().hex[:8]

    service_name = f"unknown-template-{suffix}"

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
            "owner": "platform-team",
            "repository": (
                f"https://github.com/example/"
                f"{service_name}"
            ),
            "description": (
                "Unknown template validation service"
            ),
            "template": "does-not-exist",
            "environment": "development"
        },
        timeout=20.0
    )

    assert response.status_code == 200

    result = response.json()

    assert result["template"] == "does-not-exist"
    assert result["template_status"] == "not_found"
    assert result["policy"] == "not_evaluated"
    assert result["catalog"] == "not_registered"
    assert result["workflow"] == "not_started"
    assert result["status"] == "rejected"


def test_workflow_execution_is_persisted():
    suffix = uuid.uuid4().hex[:8]

    service_name = f"workflow-persist-{suffix}"

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
            "owner": "platform-team",
            "repository": (
                f"https://github.com/example/"
                f"{service_name}"
            ),
            "description": (
                "Persistent workflow execution test"
            ),
            "template": "backend-service",
            "environment": "development"
        },
        timeout=20.0
    )

    assert response.status_code == 200

    result = response.json()

    execution_id = result[
        "workflow_execution_id"
    ]

    assert execution_id

    workflow_api = os.getenv(
        "WORKFLOW_API_URL",
        "http://localhost:8003"
    )

    execution_response = httpx.get(
        (
            f"{workflow_api}"
            f"/workflows/executions/"
            f"{execution_id}"
        ),
        timeout=10.0
    )

    assert execution_response.status_code == 200

    execution = execution_response.json()

    assert execution["execution_id"] == execution_id
    assert execution["workflow"] == "service-creation"
    assert execution["status"] == "completed"
    assert len(execution["steps"]) >= 1

def test_workflow_timeline_contains_step_transitions():
    suffix = uuid.uuid4().hex[:8]

    service_name = f"workflow-timeline-{suffix}"

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
            "owner": "platform-team",
            "repository": (
                f"https://github.com/example/"
                f"{service_name}"
            ),
            "description": (
                "Workflow timeline validation service"
            ),
            "template": "backend-service",
            "environment": "development"
        },
        timeout=20.0
    )

    assert response.status_code == 200

    result = response.json()

    assert result["workflow"] == "completed"

    execution_id = result[
        "workflow_execution_id"
    ]

    workflow_api = os.getenv(
        "WORKFLOW_API_URL",
        "http://localhost:8003"
    )

    execution_response = httpx.get(
        (
            f"{workflow_api}"
            f"/workflows/executions/"
            f"{execution_id}"
        ),
        timeout=10.0
    )

    assert execution_response.status_code == 200

    execution = execution_response.json()

    assert execution["status"] == "completed"
    assert execution["completed_at"] is not None
    assert execution["failed_at"] is None
    assert execution["error"] is None

    expected_steps = [
        "validate-request",
        "prepare-service",
        "register-service"
    ]

    actual_steps = [
        step["name"]
        for step in execution["steps"]
    ]

    assert actual_steps == expected_steps

    for step in execution["steps"]:
        assert step["status"] == "completed"
        assert step["started_at"] is not None
        assert step["completed_at"] is not None
        assert step["error"] is None

def test_failed_workflow_can_be_retried():
    workflow_api = os.getenv(
        "WORKFLOW_API_URL",
        "http://localhost:8003"
    )

    failed_response = httpx.post(
        (
            f"{workflow_api}"
            "/workflows/service-creation/execute"
        ),
        params={
            "fail_step": "prepare-service"
        },
        timeout=10.0
    )

    assert failed_response.status_code == 200

    failed = failed_response.json()

    assert failed["status"] == "failed"
    assert failed["attempt"] == 1
    assert failed["failed_at"] is not None
    assert failed["error"] is not None

    statuses = {
        step["name"]: step["status"]
        for step in failed["steps"]
    }

    assert statuses["validate-request"] == "completed"
    assert statuses["prepare-service"] == "failed"
    assert statuses["register-service"] == "pending"

    retry_response = httpx.post(
        (
            f"{workflow_api}"
            f"/workflows/executions/"
            f"{failed['execution_id']}/retry"
        ),
        timeout=10.0
    )

    assert retry_response.status_code == 200

    retried = retry_response.json()

    assert retried["status"] == "completed"
    assert retried["attempt"] == 2
    assert (
        retried["parent_execution_id"]
        == failed["execution_id"]
    )

    assert retried["execution_id"] != failed["execution_id"]

    assert all(
        step["status"] == "completed"
        for step in retried["steps"]
    )

    persisted_response = httpx.get(
        (
            f"{workflow_api}"
            f"/workflows/executions/"
            f"{retried['execution_id']}"
        ),
        timeout=10.0
    )

    assert persisted_response.status_code == 200
    assert (
        persisted_response.json()["attempt"]
        == 2
    )

def test_workflow_execution_events_are_published():
    workflow_api = os.getenv(
        "WORKFLOW_API_URL",
        "http://localhost:8003"
    )

    response = httpx.post(
        (
            f"{workflow_api}"
            "/workflows/service-creation/execute"
        ),
        timeout=10.0
    )

    assert response.status_code == 200

    execution = response.json()

    assert execution["status"] == "completed"

    events_response = httpx.get(
        f"{EVENT_API}/events",
        timeout=10.0
    )

    assert events_response.status_code == 200

    execution_events = [
        event
        for event in events_response.json()
        if event["subject"] == execution["execution_id"]
    ]

    event_types = {
        event["type"]
        for event in execution_events
    }

    assert "workflow.execution.started" in event_types
    assert "workflow.step.started" in event_types
    assert "workflow.step.completed" in event_types
    assert "workflow.execution.completed" in event_types


def test_workflow_failure_and_retry_events_are_published():
    workflow_api = os.getenv(
        "WORKFLOW_API_URL",
        "http://localhost:8003"
    )

    failed_response = httpx.post(
        (
            f"{workflow_api}"
            "/workflows/service-creation/execute"
        ),
        params={
            "fail_step": "prepare-service"
        },
        timeout=10.0
    )

    assert failed_response.status_code == 200

    failed = failed_response.json()

    retry_response = httpx.post(
        (
            f"{workflow_api}"
            f"/workflows/executions/"
            f"{failed['execution_id']}/retry"
        ),
        timeout=10.0
    )

    assert retry_response.status_code == 200

    events_response = httpx.get(
        f"{EVENT_API}/events",
        timeout=10.0
    )

    assert events_response.status_code == 200

    failed_events = [
        event
        for event in events_response.json()
        if event["subject"] == failed["execution_id"]
    ]

    event_types = {
        event["type"]
        for event in failed_events
    }

    assert "workflow.execution.failed" in event_types
    assert "workflow.step.failed" in event_types
    assert (
        "workflow.execution.retry.requested"
        in event_types
    )

def test_self_registration_cannot_escalate_role():
    suffix = uuid.uuid4().hex[:8]

    username = f"security-{suffix}"

    response = httpx.post(
        f"{IDENTITY_API}/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "integration-password",
            "team": "platform-team",
            "role": "admin"
        },
        timeout=10.0
    )

    assert response.status_code == 422


def test_runtime_dependency_readiness():
    workflow_api = os.getenv(
        "WORKFLOW_API_URL",
        "http://localhost:8003"
    )

    workflow_ready = httpx.get(
        f"{workflow_api}/ready",
        timeout=10.0
    )

    assert workflow_ready.status_code == 200

    workflow_checks = workflow_ready.json()[
        "checks"
    ]

    assert workflow_checks["database"] is True
    assert workflow_checks["event_platform"] is True

    catalog_ready = httpx.get(
        f"{CATALOG_API}/ready",
        timeout=10.0
    )

    assert catalog_ready.status_code == 200

    catalog_checks = catalog_ready.json()[
        "checks"
    ]

    assert catalog_checks["database"] is True
    assert catalog_checks["event_platform"] is True

def test_developer_portal_platform_view():
    portal_api = os.getenv(
        "PORTAL_API_URL",
        "http://localhost:8004"
    )

    status_response = httpx.get(
        f"{portal_api}/portal/status",
        timeout=10.0
    )

    assert status_response.status_code == 200

    status = status_response.json()

    assert status["total_services"] >= 6
    assert status["healthy_services"] >= 5

    templates_response = httpx.get(
        f"{portal_api}/portal/templates",
        timeout=10.0
    )

    assert templates_response.status_code == 200

    template_names = {
        template["name"]
        for template in templates_response.json()[
            "templates"
        ]
    }

    assert "backend-service" in template_names

    services_response = httpx.get(
        f"{portal_api}/portal/services",
        timeout=10.0
    )

    assert services_response.status_code == 200
    assert "services" in services_response.json()

    workflows_response = httpx.get(
        f"{portal_api}/portal/workflows",
        timeout=10.0
    )

    assert workflows_response.status_code == 200
    assert "executions" in workflows_response.json()

    events_response = httpx.get(
        f"{portal_api}/portal/events",
        timeout=10.0
    )

    assert events_response.status_code == 200
    assert "events" in events_response.json()


def test_developer_portal_service_detail():
    portal_api = os.getenv(
        "PORTAL_API_URL",
        "http://localhost:8004"
    )

    suffix = uuid.uuid4().hex[:8]

    create = httpx.post(
        f"{CATALOG_API}/catalog",
        json={
            "name": f"portal-api-{suffix}",
            "owner": "platform-team",
            "repository": (
                "https://github.com/example/"
                f"portal-api-{suffix}"
            ),
            "description": (
                "Developer portal detail test"
            ),
            "lifecycle": "created"
        },
        timeout=10.0
    )

    assert create.status_code == 201

    service_id = create.json()["id"]

    detail = httpx.get(
        (
            f"{portal_api}"
            f"/portal/services/{service_id}"
        ),
        timeout=10.0
    )

    assert detail.status_code == 200

    payload = detail.json()

    assert payload["id"] == service_id
    assert "lifecycle_history" in payload

def test_operational_metrics_and_portal_overview():
    workflow_api = os.getenv(
        "WORKFLOW_API_URL",
        "http://localhost:8003"
    )

    portal_api = os.getenv(
        "PORTAL_API_URL",
        "http://localhost:8004"
    )

    workflow_metrics = httpx.get(
        (
            f"{workflow_api}"
            "/workflows/executions/metrics"
        ),
        timeout=10.0
    )

    assert workflow_metrics.status_code == 200

    workflow_payload = workflow_metrics.json()

    assert "total" in workflow_payload
    assert "completed" in workflow_payload
    assert "failed" in workflow_payload
    assert "success_rate" in workflow_payload

    catalog_metrics = httpx.get(
        f"{CATALOG_API}/catalog/metrics",
        timeout=10.0
    )

    assert catalog_metrics.status_code == 200

    catalog_payload = catalog_metrics.json()

    assert "total_services" in catalog_payload
    assert "lifecycle" in catalog_payload

    operations = httpx.get(
        f"{portal_api}/portal/operations",
        timeout=10.0
    )

    assert operations.status_code == 200

    payload = operations.json()

    assert "platform" in payload
    assert "catalog" in payload
    assert "workflows" in payload
    assert "recent_failures" in payload
    assert "event_counts" in payload

    assert (
        payload["workflows"]["success_rate"]
        >= 0
    )

    assert (
        payload["workflows"]["success_rate"]
        <= 1
    )

def test_platform_product_summary():
    response = httpx.get(
        (
            f"{PLATFORM_API}"
            "/api/v1/platform/summary"
        ),
        timeout=10.0
    )

    assert response.status_code == 200

    payload = response.json()

    assert "services" in payload
    assert "workflows" in payload
    assert "templates" in payload
    assert "policies" in payload

    assert (
        payload["templates"]["count"]
        >= 3
    )


def test_developer_portal_dashboard():
    portal_api = os.getenv(
        "PORTAL_API_URL",
        "http://localhost:8004"
    )

    response = httpx.get(
        f"{portal_api}/portal/dashboard",
        timeout=10.0
    )

    assert response.status_code == 200

    payload = response.json()

    assert "platform" in payload
    assert "totals" in payload
    assert "services" in payload
    assert "workflows" in payload
    assert "templates" in payload
    assert "events" in payload

    assert (
        payload["totals"]["templates"]
        >= 3
    )

def test_catalog_filtering_and_owner_portal():
    portal_api = os.getenv(
        "PORTAL_API_URL",
        "http://localhost:8004"
    )

    suffix = uuid.uuid4().hex[:8]

    owner = f"owner-{suffix}"

    service_names = [
        f"owner-api-{suffix}",
        f"owner-worker-{suffix}"
    ]

    for service_name in service_names:
        response = httpx.post(
            f"{CATALOG_API}/catalog",
            json={
                "name": service_name,
                "owner": owner,
                "repository": (
                    "https://github.com/example/"
                    f"{service_name}"
                ),
                "description": (
                    "Owner filtering integration service"
                ),
                "lifecycle": "created"
            },
            timeout=10.0
        )

        assert response.status_code == 201

    filtered = httpx.get(
        f"{CATALOG_API}/catalog",
        params={
            "owner": owner
        },
        timeout=10.0
    )

    assert filtered.status_code == 200

    filtered_services = filtered.json()

    assert len(
        filtered_services
    ) == 2

    assert all(
        service["owner"] == owner
        for service in filtered_services
    )

    summary = httpx.get(
        (
            f"{CATALOG_API}"
            f"/catalog/owners/{owner}/summary"
        ),
        timeout=10.0
    )

    assert summary.status_code == 200
    assert (
        summary.json()["total_services"]
        == 2
    )

    portal = httpx.get(
        (
            f"{portal_api}"
            f"/portal/owners/{owner}"
        ),
        timeout=10.0
    )

    assert portal.status_code == 200

    payload = portal.json()

    assert payload["owner"] == owner
    assert (
        payload[
            "service_summary"
        ][
            "total_services"
        ]
        == 2
    )


def test_workflow_execution_filters():
    workflow_api = os.getenv(
        "WORKFLOW_API_URL",
        "http://localhost:8003"
    )

    response = httpx.get(
        (
            f"{workflow_api}"
            "/workflows/executions"
        ),
        params={
            "workflow": "service-creation",
            "limit": 10
        },
        timeout=10.0
    )

    assert response.status_code == 200

    executions = response.json()

    assert len(
        executions
    ) <= 10

    assert all(
        execution["workflow"]
        == "service-creation"
        for execution in executions
    )

def test_template_rendering_and_provisioning_materialization():
    template_api = os.getenv(
        "TEMPLATE_API_URL",
        "http://localhost:8002"
    )

    suffix = uuid.uuid4().hex[:8]

    service_name = f"render-api-{suffix}"

    render = httpx.post(
        (
            f"{template_api}"
            "/templates/backend-service/render"
        ),
        json={
            "name": service_name,
            "owner": "platform-team",
            "repository": (
                "https://github.com/example/"
                f"{service_name}"
            ),
            "environment": "development"
        },
        timeout=10.0
    )

    assert render.status_code == 200

    rendered = render.json()

    assert rendered["template"] == "backend-service"
    assert "README.md" in rendered["files"]
    assert "service.yaml" in rendered["files"]
    assert "app/main.py" in rendered["files"]

    session = create_authenticated_session()

    provision = httpx.post(
        (
            f"{PLATFORM_API}"
            "/api/v1/provision/services"
        ),
        headers={
            "Authorization": (
                f"Bearer "
                f"{session['access_token']}"
            )
        },
        json={
            "name": service_name,
            "owner": "platform-team",
            "repository": (
                "https://github.com/example/"
                f"{service_name}"
            ),
            "description": (
                "Rendered golden path integration test"
            ),
            "template": "backend-service",
            "environment": "development"
        },
        timeout=20.0
    )

    assert provision.status_code == 200

    payload = provision.json()

    assert (
        payload["rendered_template"]["template"]
        == "backend-service"
    )

    assert (
        "app/main.py"
        in payload["rendered_template"]["files"]
    )


def test_portal_template_preview():
    portal_api = os.getenv(
        "PORTAL_API_URL",
        "http://localhost:8004"
    )

    suffix = uuid.uuid4().hex[:8]

    preview = httpx.post(
        (
            f"{portal_api}"
            "/portal/templates/backend-service/preview"
        ),
        json={
            "name": f"preview-{suffix}",
            "owner": "platform-team",
            "repository": (
                "https://github.com/example/"
                f"preview-{suffix}"
            ),
            "environment": "development"
        },
        timeout=10.0
    )

    assert preview.status_code == 200

    payload = preview.json()

    assert payload["template"] == "backend-service"
    assert "service.yaml" in payload["files"]

def test_scaffold_manifest_contract():
    template_api = os.getenv(
        "TEMPLATE_API_URL",
        "http://localhost:8002"
    )

    suffix = uuid.uuid4().hex[:8]

    response = httpx.post(
        (
            f"{template_api}"
            "/templates/backend-service/render"
        ),
        json={
            "name": f"manifest-{suffix}",
            "owner": "platform-team",
            "repository": (
                "https://github.com/example/"
                f"manifest-{suffix}"
            ),
            "environment": "development"
        },
        timeout=10.0
    )

    assert response.status_code == 200

    payload = response.json()

    manifest = payload["manifest"]

    assert (
        manifest["api_version"]
        == "platform.internal/v1"
    )

    assert (
        manifest["kind"]
        == "ServiceScaffold"
    )

    assert (
        manifest["template"]["name"]
        == "backend-service"
    )

    assert (
        manifest["artifact"]["file_count"]
        >= 4
    )

    assert (
        manifest["artifact"][
            "checksum_algorithm"
        ]
        == "sha256"
    )

    assert len(
        manifest["artifact"]["checksum"]
    ) == 64


def test_provisioning_returns_artifact_manifest():
    suffix = uuid.uuid4().hex[:8]

    service_name = (
        f"artifact-{suffix}"
    )

    session = create_authenticated_session()

    response = httpx.post(
        (
            f"{PLATFORM_API}"
            "/api/v1/provision/services"
        ),
        headers={
            "Authorization": (
                f"Bearer "
                f"{session['access_token']}"
            )
        },
        json={
            "name": service_name,
            "owner": "platform-team",
            "repository": (
                "https://github.com/example/"
                f"{service_name}"
            ),
            "description": (
                "Artifact contract integration test"
            ),
            "template": "backend-service",
            "environment": "development"
        },
        timeout=20.0
    )

    assert response.status_code == 200

    payload = response.json()

    manifest = payload[
        "artifact_manifest"
    ]

    assert manifest is not None

    assert (
        manifest["metadata"]["name"]
        == service_name
    )

    assert (
        manifest["artifact"]["file_count"]
        >= 4
    )


def test_portal_scaffold_preview():
    portal_api = os.getenv(
        "PORTAL_API_URL",
        "http://localhost:8004"
    )

    suffix = uuid.uuid4().hex[:8]

    response = httpx.post(
        (
            f"{portal_api}"
            "/portal/scaffolds/"
            "backend-service/preview"
        ),
        json={
            "name": f"portal-scaffold-{suffix}",
            "owner": "platform-team",
            "repository": (
                "https://github.com/example/"
                f"portal-scaffold-{suffix}"
            ),
            "environment": "development"
        },
        timeout=10.0
    )

    assert response.status_code == 200

    payload = response.json()

    assert "manifest" in payload
    assert "checksum" in payload
    assert "Dockerfile" in payload["files"]

def test_portal_self_service_requires_authentication():
    portal_api = os.getenv(
        "PORTAL_API_URL",
        "http://localhost:8004"
    )

    response = httpx.post(
        (
            f"{portal_api}"
            "/portal/services/provision"
        ),
        json={
            "name": "unauthorized-service",
            "owner": "platform-team",
            "repository": (
                "https://github.com/example/"
                "unauthorized-service"
            ),
            "description": (
                "Unauthorized provisioning should fail"
            ),
            "template": "backend-service",
            "environment": "development"
        },
        timeout=10.0
    )

    assert response.status_code == 401


def test_portal_self_service_provisioning():
    portal_api = os.getenv(
        "PORTAL_API_URL",
        "http://localhost:8004"
    )

    suffix = uuid.uuid4().hex[:8]

    service_name = (
        f"portal-create-{suffix}"
    )

    session = create_authenticated_session()

    response = httpx.post(
        (
            f"{portal_api}"
            "/portal/services/provision"
        ),
        headers={
            "Authorization": (
                f"Bearer "
                f"{session['access_token']}"
            )
        },
        json={
            "name": service_name,
            "owner": "platform-team",
            "repository": (
                "https://github.com/example/"
                f"{service_name}"
            ),
            "description": (
                "Developer portal self service "
                "provisioning integration test"
            ),
            "template": "backend-service",
            "environment": "development"
        },
        timeout=20.0
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["service"] == service_name
    assert payload["policy"] == "allowed"
    assert payload["catalog"] == "registered"

    assert (
        payload["template_status"]
        == "resolved"
    )

    assert (
        payload["artifact_manifest"]
        is not None
    )

    assert (
        payload["workflow_execution_id"]
        is not None
    )

    catalog_response = httpx.get(
        f"{CATALOG_API}/catalog",
        params={
            "owner": "platform-team"
        },
        timeout=10.0
    )

    assert catalog_response.status_code == 200

    names = {
        service["name"]
        for service
        in catalog_response.json()
    }

    assert service_name in names