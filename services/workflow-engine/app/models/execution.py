from datetime import datetime

from pydantic import BaseModel


class WorkflowStep(BaseModel):
    name: str
    status: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None


class WorkflowExecution(BaseModel):
    execution_id: str
    workflow: str
    status: str
    attempt: int
    parent_execution_id: str | None = None
    service_id: int | None = None
    service_name: str | None = None
    owner: str | None = None
    steps: list[WorkflowStep]
    started_at: datetime
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    error: str | None = None