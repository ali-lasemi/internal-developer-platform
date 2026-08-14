from datetime import datetime

from pydantic import BaseModel


class WorkflowStep(BaseModel):
    name: str
    status: str


class WorkflowExecution(BaseModel):
    execution_id: str
    workflow: str
    status: str
    steps: list[WorkflowStep]
    started_at: datetime
    completed_at: datetime | None = None