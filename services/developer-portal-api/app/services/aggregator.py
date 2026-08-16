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

def _score_component(
    condition: bool,
    points: int
):
    return points if condition else 0


async def service_scorecard(
    service_id: int
):
    service = await service_detail(
        service_id
    )

    workflows = await workflow_executions()

    service_name = service.get(
        "name"
    )

    repository = service.get(
        "repository"
    )

    owner = service.get(
        "owner"
    )

    lifecycle = service.get(
        "lifecycle"
    )

    description = service.get(
        "description"
    )

    lifecycle_history = service.get(
        "lifecycle_history",
        []
    )

    related_workflows = [
        execution
        for execution in workflows
        if execution.get(
            "workflow"
        ) == "service-creation"
    ]

    failed_workflows = [
        execution
        for execution in related_workflows
        if execution.get(
            "status"
        ) == "failed"
    ]

    checks = {
        "ownership": {
            "passed": bool(
                owner
            ),
            "weight": 20
        },
        "repository": {
            "passed": bool(
                repository
            ),
            "weight": 20
        },
        "documentation": {
            "passed": bool(
                description
            ),
            "weight": 15
        },
        "managed_lifecycle": {
            "passed": lifecycle in {
                "created",
                "development",
                "production",
                "deprecated",
                "retired"
            },
            "weight": 15
        },
        "lifecycle_history": {
            "passed": len(
                lifecycle_history
            ) > 0,
            "weight": 10
        },
        "workflow_health": {
            "passed": len(
                failed_workflows
            ) == 0,
            "weight": 20
        }
    }

    score = sum(
        _score_component(
            check[
                "passed"
            ],
            check[
                "weight"
            ]
        )
        for check in checks.values()
    )

    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    else:
        grade = "D"

    return {
        "service_id": service_id,
        "service": service_name,
        "owner": owner,
        "score": score,
        "grade": grade,
        "checks": checks
    }


async def platform_scorecards():
    services = await catalog_services()

    results = []

    for service in services[:100]:
        results.append(
            await service_scorecard(
                service[
                    "id"
                ]
            )
        )

    if results:
        average_score = round(
            sum(
                item["score"]
                for item in results
            )
            / len(
                results
            ),
            2
        )
    else:
        average_score = 100.0

    grades = {}

    for result in results:
        grade = result[
            "grade"
        ]

        grades[
            grade
        ] = grades.get(
            grade,
            0
        ) + 1

    return {
        "total_services": len(
            results
        ),
        "average_score": average_score,
        "grades": grades,
        "services": results
    }

async def service_quality_gate(
    service_id: int,
    minimum_score: int = 75
):
    minimum_score = min(
        max(
            minimum_score,
            0
        ),
        100
    )

    scorecard = await service_scorecard(
        service_id
    )

    failed_checks = [
        name
        for name, check
        in scorecard[
            "checks"
        ].items()
        if not check[
            "passed"
        ]
    ]

    passed = (
        scorecard[
            "score"
        ]
        >= minimum_score
    )

    return {
        "service_id": service_id,
        "service": scorecard[
            "service"
        ],
        "score": scorecard[
            "score"
        ],
        "grade": scorecard[
            "grade"
        ],
        "minimum_score": minimum_score,
        "passed": passed,
        "decision": (
            "allowed"
            if passed
            else "blocked"
        ),
        "failed_checks": failed_checks
    }


async def platform_quality_report(
    minimum_score: int = 75
):
    minimum_score = min(
        max(
            minimum_score,
            0
        ),
        100
    )

    scorecards = await platform_scorecards()

    gates = []

    for service in scorecards[
        "services"
    ]:
        gates.append(
            await service_quality_gate(
                service[
                    "service_id"
                ],
                minimum_score
            )
        )

    passing = sum(
        1
        for gate in gates
        if gate[
            "passed"
        ]
    )

    blocked = len(
        gates
    ) - passing

    compliance_rate = (
        round(
            passing / len(
                gates
            ),
            4
        )
        if gates
        else 1.0
    )

    return {
        "minimum_score": minimum_score,
        "total_services": len(
            gates
        ),
        "passing_services": passing,
        "blocked_services": blocked,
        "compliance_rate": compliance_rate,
        "gates": gates
    }

async def promote_service(
    service_id: int,
    target: str,
    minimum_score: int = 75,
    dry_run: bool = False
):
    service = await service_detail(
        service_id
    )

    gate = await service_quality_gate(
        service_id,
        minimum_score
    )

    current = service.get(
        "lifecycle"
    )

    if not gate[
        "passed"
    ]:
        return {
            "allowed": False,
            "dry_run": dry_run,
            "service_id": service_id,
            "service": service.get(
                "name"
            ),
            "current_lifecycle": current,
            "target_lifecycle": target,
            "quality_gate": gate,
            "transition": None
        }

    if dry_run:
        return {
            "allowed": True,
            "dry_run": True,
            "service_id": service_id,
            "service": service.get(
                "name"
            ),
            "current_lifecycle": current,
            "target_lifecycle": target,
            "quality_gate": gate,
            "transition": None
        }

    result = await post_json(
        (
            f"{CATALOG_URL}"
            f"/catalog/{service_id}/lifecycle"
        ),
        {
            "lifecycle": target
        }
    )

    return {
        "allowed": True,
        "dry_run": False,
        "service_id": service_id,
        "service": service.get(
            "name"
        ),
        "current_lifecycle": current,
        "target_lifecycle": target,
        "quality_gate": gate,
        "transition": result
    }