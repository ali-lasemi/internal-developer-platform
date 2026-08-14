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


def _utcnow():
    return datetime.now(
        timezone.utc
    )


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
                status=step["status"],
                started_at=step.get(
                    "started_at"
                ),
                completed_at=step.get(
                    "completed_at"
                ),
                error=step.get(
                    "error"
                )
            )
            for step in record.steps
        ],
        started_at=record.started_at,
        completed_at=record.completed_at,
        failed_at=record.failed_at,
        error=record.error
    )


def _persist(
    database: Session,
    record: WorkflowExecutionRecord
):
    database.add(
        record
    )

    database.commit()
    database.refresh(
        record
    )


def execute_workflow(
    database: Session,
    workflow_name: str
) -> WorkflowExecution:
    execution_id = uuid4().hex

    step_names = WORKFLOW_STEPS.get(
        workflow_name,
        [
            "execute"
        ]
    )

    steps = [
        {
            "name": name,
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "error": None
        }
        for name in step_names
    ]

    record = WorkflowExecutionRecord(
        execution_id=execution_id,
        workflow=workflow_name,
        status="pending",
        steps=steps,
        started_at=_utcnow(),
        completed_at=None,
        failed_at=None,
        error=None
    )

    _persist(
        database,
        record
    )

    record.status = "running"

    _persist(
        database,
        record
    )

    try:
        current_steps = list(
            record.steps
        )

        for index, step in enumerate(
            current_steps
        ):
            started_at = _utcnow()

            current_steps[index] = {
                **step,
                "status": "running",
                "started_at": started_at.isoformat(),
                "completed_at": None,
                "error": None
            }

            record.steps = list(
                current_steps
            )

            _persist(
                database,
                record
            )

            completed_at = _utcnow()

            current_steps[index] = {
                **current_steps[index],
                "status": "completed",
                "completed_at": (
                    completed_at.isoformat()
                )
            }

            record.steps = list(
                current_steps
            )

            _persist(
                database,
                record
            )

        record.status = "completed"
        record.completed_at = _utcnow()

        _persist(
            database,
            record
        )

    except Exception as exc:
        record.status = "failed"
        record.failed_at = _utcnow()
        record.error = str(
            exc
        )

        current_steps = list(
            record.steps
        )

        for index, step in enumerate(
            current_steps
        ):
            if step["status"] == "running":
                current_steps[index] = {
                    **step,
                    "status": "failed",
                    "error": str(
                        exc
                    )
                }

                break

        record.steps = current_steps

        _persist(
            database,
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