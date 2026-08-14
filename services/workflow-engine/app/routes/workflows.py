from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
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
    database: Session = Depends(
        get_db
    )
):
    return list_executions(
        database
    )


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