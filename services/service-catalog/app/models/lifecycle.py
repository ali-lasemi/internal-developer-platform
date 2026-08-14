from pydantic import BaseModel
from pydantic import Field


class LifecycleTransitionRequest(BaseModel):
    lifecycle: str = Field(
        min_length=2,
        max_length=50
    )


class LifecycleTransitionResponse(BaseModel):
    id: int
    name: str
    previous_lifecycle: str
    lifecycle: str
