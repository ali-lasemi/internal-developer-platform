from fastapi import APIRouter
from fastapi import HTTPException

from app.models.execution import WorkflowExecution
from app.models.workflow import Workflow
from app.services.execution import execute_workflow
from app.services.execution import get_execution


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
    name: str
):
    return execute_workflow(
        name
    )


@router.get(
    "/executions/{execution_id}",
    response_model=WorkflowExecution
)
def read_execution(
    execution_id: str
):
    execution = get_execution(
        execution_id
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Workflow execution not found"
        )

    return execution