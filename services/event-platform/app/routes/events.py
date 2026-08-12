from fastapi import APIRouter
from fastapi import HTTPException

from app.adapters.redis_bus import event_bus
from app.models.event import PlatformEvent
from app.models.event import PlatformEventCreate
from app.models.event import create_event
from app.repositories.event_repository import event_repository


router = APIRouter(
    prefix="/events",
    tags=["events"]
)


@router.get(
    "",
    response_model=list[PlatformEvent]
)
def list_events():
    return event_repository.list()


@router.post(
    "",
    response_model=PlatformEvent,
    status_code=201
)
async def publish_event(
    payload: PlatformEventCreate
):
    event = create_event(payload)

    try:
        await event_bus.publish(event)

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Event bus unavailable: {exc}"
        ) from exc

    return event_repository.add(event)
