from datetime import datetime
from datetime import timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import WorkflowExecutionRecord
from app.models.execution import WorkflowExecution
from app.models.execution import WorkflowStep


WORKFLOW_STEPS = {
    "service-creation": [
        "validate-request",
        "prepare-service",
        "register-service"
    ]
}


def _to_model(
    record: WorkflowExecutionRecord
) -> WorkflowExecution:
    return WorkflowExecution(
        execution_id=record.execution_id,
        workflow=record.workflow,
        status=record.status,
        steps=[
            WorkflowStep(
                name=step["name"],
                status=step["status"]
            )
            for step in record.steps
        ],
        started_at=record.started_at,
        completed_at=record.completed_at
    )


def execute_workflow(
    database: Session,
    workflow_name: str
) -> WorkflowExecution:
    execution_id = uuid4().hex

    steps = [
        {
            "name": name,
            "status": "completed"
        }
        for name in WORKFLOW_STEPS.get(
            workflow_name,
            [
                "execute"
            ]
        )
    ]

    now = datetime.now(
        timezone.utc
    )

    record = WorkflowExecutionRecord(
        execution_id=execution_id,
        workflow=workflow_name,
        status="completed",
        steps=steps,
        started_at=now,
        completed_at=now
    )

    database.add(
        record
    )

    database.commit()
    database.refresh(
        record
    )

    return _to_model(
        record
    )


def get_execution(
    database: Session,
    execution_id: str
) -> WorkflowExecution | None:
    record = (
        database
        .query(WorkflowExecutionRecord)
        .filter(
            WorkflowExecutionRecord.execution_id
            == execution_id
        )
        .first()
    )

    if record is None:
        return None

    return _to_model(
        record
    )


def list_executions(
    database: Session
) -> list[WorkflowExecution]:
    records = (
        database
        .query(WorkflowExecutionRecord)
        .order_by(
            WorkflowExecutionRecord.id.desc()
        )
        .all()
    )

    return [
        _to_model(record)
        for record in records
    ]