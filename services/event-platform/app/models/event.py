from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class PlatformEventCreate(BaseModel):
    type: str = Field(min_length=3, max_length=120)
    source: str = Field(min_length=2, max_length=120)
    subject: str = Field(min_length=1, max_length=255)
    data: dict = Field(default_factory=dict)


class PlatformEvent(PlatformEventCreate):
    id: UUID
    occurred_at: datetime


def create_event(payload: PlatformEventCreate) -> PlatformEvent:
    return PlatformEvent(
        id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        **payload.model_dump()
    )
