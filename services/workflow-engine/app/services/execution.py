from datetime import datetime
from datetime import timezone
from uuid import uuid4

from app.models.execution import WorkflowExecution
from app.models.execution import WorkflowStep


executions: dict[str, WorkflowExecution] = {}


WORKFLOW_STEPS = {
    "service-creation": [
        "validate-request",
        "prepare-service",
        "register-service"
    ]
}


def execute_workflow(
    workflow_name: str
) -> WorkflowExecution:
    execution_id = uuid4().hex

    steps = [
        WorkflowStep(
            name=name,
            status="completed"
        )
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

    execution = WorkflowExecution(
        execution_id=execution_id,
        workflow=workflow_name,
        status="completed",
        steps=steps,
        started_at=now,
        completed_at=now
    )

    executions[
        execution_id
    ] = execution

    return execution


def get_execution(
    execution_id: str
) -> WorkflowExecution | None:
    return executions.get(
        execution_id
    )