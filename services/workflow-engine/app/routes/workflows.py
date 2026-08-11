from fastapi import APIRouter
from app.models.workflow import Workflow

router = APIRouter(
    prefix="/workflows",
    tags=["workflows"]
)


workflows = []


@router.get("")
def list_workflows():
    return workflows


@router.post("")
def register_workflow(workflow: Workflow):
    workflows.append(workflow)
    return workflow


@router.post("/{name}/execute")
def execute_workflow(name: str):
    return {
        "workflow": name,
        "status": "started"
    }
