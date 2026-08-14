from fastapi import APIRouter
from fastapi import HTTPException

from app.models.portal import PortalAction
from app.services.aggregator import catalog_services
from app.services.aggregator import developer_dashboard
from app.services.aggregator import operational_overview
from app.services.aggregator import owner_view
from app.services.aggregator import platform_status
from app.services.aggregator import recent_events
from app.services.aggregator import service_detail
from app.services.aggregator import templates
from app.services.aggregator import workflow_execution
from app.services.aggregator import workflow_executions


router = APIRouter(
    prefix="/portal",
    tags=["portal"]
)


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