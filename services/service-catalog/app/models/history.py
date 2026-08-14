from datetime import datetime

from pydantic import BaseModel
from pydantic import ConfigDict


class LifecycleHistoryEntry(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    service_id: int
    previous_lifecycle: str
    lifecycle: str
    changed_at: datetime
