import asyncio

from app.clients.platform import CATALOG_URL
from app.clients.platform import EVENT_URL
from app.clients.platform import PLATFORM_API_URL
from app.clients.platform import POLICY_URL
from app.clients.platform import TEMPLATE_URL
from app.clients.platform import WORKFLOW_URL
from app.clients.platform import get_json
from app.clients.platform import post_json
from app.clients.platform import post_json_with_headers
from app.clients.platform import service_status


async def platform_status():
    services = await asyncio.gather(
        service_status(
            "platform-api",
            PLATFORM_API_URL
        ),
        service_status(
            "service-catalog",
            CATALOG_URL
        ),
        service_status(
            "template-engine",
            TEMPLATE_URL
        ),
        service_status(
            "workflow-engine",
            WORKFLOW_URL
        ),
        service_status(
            "policy-engine",
            POLICY_URL
        ),
        service_status(
            "event-platform",
            EVENT_URL
        )
    )

    healthy = sum(
        1
        for service in services
        if service["status"] == "healthy"
    )

    return {
        "status": (
            "healthy"
            if healthy == len(services)
            else "degraded"
        ),
        "healthy_services": healthy,
        "total_services": len(
            services
        ),
        "services": services
    }


async def catalog_services():
    return await get_json(
        f"{CATALOG_URL}/catalog"
    )


async def service_detail(
    service_id: int
):
    service = await get_json(
        f"{CATALOG_URL}/catalog/{service_id}"
    )

    history = await get_json(
        (
            f"{CATALOG_URL}"
            f"/catalog/{service_id}"
            "/lifecycle/history"
        )
    )

    return {
        **service,
        "lifecycle_history": history
    }


async def workflow_executions():
    return await get_json(
        f"{WORKFLOW_URL}/workflows/executions"
    )


async def workflow_execution(
    execution_id: str
):
    return await get_json(
        (
            f"{WORKFLOW_URL}"
            f"/workflows/executions/"
            f"{execution_id}"
        )
    )


async def templates():
    return await get_json(
        f"{TEMPLATE_URL}/templates"
    )


async def recent_events():
    events = await get_json(
        f"{EVENT_URL}/events"
    )

    return events[-50:]

async def operational_overview():
    (
        status,
        catalog_metrics,
        workflow_metrics,
        workflow_history,
        events
    ) = await asyncio.gather(
        platform_status(),
        get_json(
            f"{CATALOG_URL}/catalog/metrics"
        ),
        get_json(
            (
                f"{WORKFLOW_URL}"
                "/workflows/executions/metrics"
            )
        ),
        workflow_executions(),
        recent_events()
    )

    recent_failures = [
        execution
        for execution in workflow_history
        if execution.get(
            "status"
        ) == "failed"
    ][:20]

    event_counts = {}

    for event in events:
        event_type = event.get(
            "type",
            "unknown"
        )

        event_counts[event_type] = (
            event_counts.get(
                event_type,
                0
            )
            + 1
        )

    return {
        "platform": status,
        "catalog": catalog_metrics,
        "workflows": workflow_metrics,
        "recent_failures": recent_failures,
        "event_counts": event_counts,
        "recent_event_count": len(
            events
        )
    }

async def developer_dashboard():
    (
        platform,
        services,
        workflows,
        template_items,
        events
    ) = await asyncio.gather(
        platform_status(),
        catalog_services(),
        workflow_executions(),
        templates(),
        recent_events()
    )

    production_services = [
        service
        for service in services
        if service.get(
            "lifecycle"
        ) == "production"
    ]

    failed_workflows = [
        execution
        for execution in workflows
        if execution.get(
            "status"
        ) == "failed"
    ]

    return {
        "platform": platform,
        "totals": {
            "services": len(
                services
            ),
            "production_services": len(
                production_services
            ),
            "workflow_executions": len(
                workflows
            ),
            "failed_workflows": len(
                failed_workflows
            ),
            "templates": len(
                template_items
            ),
            "recent_events": len(
                events
            )
        },
        "services": services[-20:],
        "workflows": workflows[:20],
        "templates": template_items,
        "events": events[-20:]
    }

async def owner_view(
    owner: str
):
    services = await get_json(
        (
            f"{CATALOG_URL}"
            f"/catalog/owners/{owner}/summary"
        )
    )

    workflows = await workflow_executions()

    events = await recent_events()

    owner_services = {
        service["name"]
        for service in services[
            "services"
        ]
    }

    relevant_events = [
        event
        for event in events
        if (
            event.get(
                "subject"
            )
            in owner_services
            or event.get(
                "data",
                {}
            ).get(
                "owner"
            )
            == owner
        )
    ]

    return {
        "owner": owner,
        "service_summary": services,
        "workflow_summary": {
            "total": len(
                workflows
            ),
            "failed": len(
                [
                    item
                    for item in workflows
                    if item.get(
                        "status"
                    )
                    == "failed"
                ]
            )
        },
        "recent_events": relevant_events[
            -20:
        ]
    }

async def template_preview(
    template_name: str,
    payload: dict
):
    return await post_json(
        (
            f"{TEMPLATE_URL}"
            f"/templates/{template_name}/render"
        ),
        payload
    )

async def scaffold_preview(
    template_name: str,
    payload: dict
):
    rendered = await template_preview(
        template_name,
        payload
    )

    return {
        "template": rendered[
            "template"
        ],
        "version": rendered[
            "version"
        ],
        "service": rendered[
            "service"
        ],
        "manifest": rendered[
            "manifest"
        ],
        "checksum": rendered[
            "checksum"
        ],
        "files": list(
            rendered[
                "files"
            ].keys()
        )
    }

async def provision_from_portal(
    payload: dict,
    authorization: str
):
    response = await post_json_with_headers(
        (
            f"{PLATFORM_API_URL}"
            "/api/v1/provision/services"
        ),
        payload,
        {
            "Authorization": authorization
        }
    )

    return {
        "status_code": response.status_code,
        "payload": response.json()
    }