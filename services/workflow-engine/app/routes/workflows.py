from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import WorkflowExecutionRecord
from app.models.execution import WorkflowExecution
from app.models.workflow import Workflow
from app.services.execution import execute_workflow
from app.services.execution import get_execution
from app.services.execution import list_executions
from app.services.execution import retry_execution


router = APIRouter(
    prefix="/workflows",
    tags=["workflows"]
)


workflows = []


@router.get("")
def list_workflows():
    return workflows


@router.post("")
def register_workflow(
    workflow: Workflow
):
    workflows.append(
        workflow
    )

    return workflow


@router.post(
    "/{name}/execute",
    response_model=WorkflowExecution
)
def start_workflow(
    name: str,
    fail_step: str | None = None,
    database: Session = Depends(
        get_db
    )
):
    return execute_workflow(
        database=database,
        workflow_name=name,
        fail_step=fail_step
    )


@router.get(
    "/executions",
    response_model=list[WorkflowExecution]
)
def read_executions(
    status: str | None = None,
    workflow: str | None = None,
    limit: int = 100,
    database: Session = Depends(
        get_db
    )
):
    query = database.query(
        WorkflowExecutionRecord
    )

    if status:
        query = query.filter(
            WorkflowExecutionRecord.status
            == status
        )

    if workflow:
        query = query.filter(
            WorkflowExecutionRecord.workflow
            == workflow
        )

    safe_limit = min(
        max(
            limit,
            1
        ),
        500
    )

    records = (
        query
        .order_by(
            WorkflowExecutionRecord.id.desc()
        )
        .limit(
            safe_limit
        )
        .all()
    )

    return [
        get_execution(
            database,
            record.execution_id
        )
        for record in records
    ]


@router.get(
    "/executions/metrics"
)
def execution_metrics(
    database: Session = Depends(
        get_db
    )
):
    total = (
        database
        .query(
            func.count(
                WorkflowExecutionRecord.id
            )
        )
        .scalar()
        or 0
    )

    rows = (
        database
        .query(
            WorkflowExecutionRecord.status,
            func.count(
                WorkflowExecutionRecord.id
            )
        )
        .group_by(
            WorkflowExecutionRecord.status
        )
        .all()
    )

    statuses = {
        status: count
        for status, count in rows
    }

    completed = statuses.get(
        "completed",
        0
    )

    failed = statuses.get(
        "failed",
        0
    )

    success_rate = (
        round(
            completed / total,
            4
        )
        if total
        else 1.0
    )

    return {
        "total": total,
        "completed": completed,
        "failed": failed,
        "running": statuses.get(
            "running",
            0
        ),
        "pending": statuses.get(
            "pending",
            0
        ),
        "success_rate": success_rate
    }


@router.get(
    "/executions/{execution_id}",
    response_model=WorkflowExecution
)
def read_execution(
    execution_id: str,
    database: Session = Depends(
        get_db
    )
):
    execution = get_execution(
        database,
        execution_id
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow execution not found"
        )

    return execution


@router.post(
    "/executions/{execution_id}/retry",
    response_model=WorkflowExecution
)
def retry_workflow(
    execution_id: str,
    database: Session = Depends(
        get_db
    )
):
    try:
        execution = retry_execution(
            database,
            execution_id
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(
                exc
            )
        ) from exc

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow execution not found"
        )

    return execution