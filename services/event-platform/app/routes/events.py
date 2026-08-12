from fastapi import APIRouter

from app.bus.publisher import publisher
from app.models.event import PlatformEvent
from app.models.event import PlatformEventCreate
from app.models.event import create_event


router = APIRouter(
    prefix="/events",
    tags=["events"]
)


@router.get(
    "",
    response_model=list[PlatformEvent]
)
def list_events():
    return publisher.list_events()


@router.post(
    "",
    response_model=PlatformEvent,
    status_code=201
)
def publish_event(payload: PlatformEventCreate):
    event = create_event(payload)
    return publisher.publish(event)
