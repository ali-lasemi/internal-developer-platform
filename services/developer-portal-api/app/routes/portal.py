from fastapi import APIRouter
from app.models.portal import PortalAction

router = APIRouter(
    prefix="/portal",
    tags=["portal"]
)


@router.get("/services")
def services():
    return {
        "services": [
            "platform-api",
            "service-catalog",
            "template-engine",
            "workflow-engine"
        ]
    }


@router.post("/actions")
def create_action(action: PortalAction):
    return {
        "status": "accepted",
        "service": action.service,
        "action": action.action
    }
