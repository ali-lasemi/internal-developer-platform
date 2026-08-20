from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Header

from app.models.portal import PortalAction
from app.services.aggregator import catalog_services
from app.services.aggregator import developer_dashboard
from app.services.aggregator import operational_overview
from app.services.aggregator import owner_view
from app.services.aggregator import platform_status
from app.services.aggregator import provision_from_portal
from app.services.aggregator import authorized_provision_from_portal
from app.services.aggregator import current_identity
from app.services.aggregator import promote_service
from app.services.aggregator import recent_events
from app.services.aggregator import service_detail
from app.services.aggregator import service_scorecard
from app.services.aggregator import service_quality_gate
from app.services.aggregator import platform_scorecards
from app.services.aggregator import platform_quality_report
from app.services.aggregator import templates
from app.services.aggregator import scaffold_preview
from app.services.aggregator import template_preview
from app.services.aggregator import workflow_execution
from app.services.aggregator import workflow_executions


router = APIRouter(
    prefix="/portal",
    tags=["portal"]
)


@router.get(
    "/me"
)
async def me(
    authorization: str | None = Header(
        default=None
    )
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )

    result = await current_identity(
        authorization
    )

    status_code = result[
        "status_code"
    ]

    payload = result[
        "payload"
    ]

    if status_code >= 400:
        raise HTTPException(
            status_code=status_code,
            detail=payload.get(
                "detail",
                payload
            )
        )

    return payload


@router.get("/status")
async def status():
    return await platform_status()


@router.get("/dashboard")
async def dashboard():
    return await developer_dashboard()


@router.get("/operations")
async def operations():
    return await operational_overview()


@router.get("/services")
async def services():
    return {
        "services": await catalog_services()
    }


@router.get("/services/{service_id}")
async def service(
    service_id: int
):
    try:
        return await service_detail(
            service_id
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(
                exc
            )
        ) from exc


@router.get("/workflows")
async def workflows():
    return {
        "executions": await workflow_executions()
    }


@router.get(
    "/workflows/{execution_id}"
)
async def workflow(
    execution_id: str
):
    try:
        return await workflow_execution(
            execution_id
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(
                exc
            )
        ) from exc


@router.get("/templates")
async def list_templates():
    return {
        "templates": await templates()
    }


@router.get("/events")
async def events():
    return {
        "events": await recent_events()
    }


@router.post("/actions")
def create_action(
    action: PortalAction
):
    return {
        "status": "accepted",
        "service": action.service,
        "action": action.action
    }

@router.get(
    "/owners/{owner}"
)
async def owner_dashboard(
    owner: str
):
    return await owner_view(
        owner
    )

@router.post(
    "/templates/{template_name}/preview"
)
async def preview_template(
    template_name: str,
    payload: dict
):
    try:
        return await template_preview(
            template_name,
            payload
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(
                exc
            )
        ) from exc

@router.post(
    "/scaffolds/{template_name}/preview"
)
async def preview_scaffold(
    template_name: str,
    payload: dict
):
    try:
        return await scaffold_preview(
            template_name,
            payload
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(
                exc
            )
        ) from exc

@router.post(
    "/services/provision"
)
async def provision_service(
    payload: dict,
    authorization: str | None = Header(
        default=None
    )
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )

    result = await authorized_provision_from_portal(
        payload,
        authorization
    )

    status_code = result[
        "status_code"
    ]

    response_payload = result[
        "payload"
    ]

    if status_code >= 400:
        raise HTTPException(
            status_code=status_code,
            detail=response_payload
        )

    return response_payload

@router.get(
    "/services/{service_id}/scorecard"
)
async def scorecard(
    service_id: int
):
    try:
        return await service_scorecard(
            service_id
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(
                exc
            )
        ) from exc


@router.get(
    "/scorecards"
)
async def scorecards():
    return await platform_scorecards()

@router.get(
    "/services/{service_id}/quality-gate"
)
async def quality_gate(
    service_id: int,
    minimum_score: int = 75
):
    try:
        return await service_quality_gate(
            service_id,
            minimum_score
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(
                exc
            )
        ) from exc


@router.get(
    "/quality-report"
)
async def quality_report(
    minimum_score: int = 75
):
    return await platform_quality_report(
        minimum_score
    )

@router.post(
    "/services/{service_id}/promote"
)
async def promote(
    service_id: int,
    target: str,
    minimum_score: int = 75,
    dry_run: bool = False
):
    try:
        result = await promote_service(
            service_id,
            target,
            minimum_score,
            dry_run
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(
                exc
            )
        ) from exc

    if not result[
        "allowed"
    ]:
        raise HTTPException(
            status_code=409,
            detail=result
        )

    return result