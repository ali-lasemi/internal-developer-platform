from fastapi import APIRouter
from fastapi import HTTPException

from app.models.template import Template
from app.models.template import TemplateResolution
from app.services.registry import list_templates
from app.services.registry import resolve_template


router = APIRouter(
    prefix="/templates",
    tags=["templates"]
)


@router.get(
    "",
    response_model=list[Template]
)
def get_templates():
    return list_templates()


@router.get(
    "/{template_name}",
    response_model=TemplateResolution
)
def get_template(
    template_name: str
):
    template = resolve_template(
        template_name
    )

    if template is None:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    return TemplateResolution(
        name=template.name,
        version=template.version,
        type=template.type
    )


@router.post(
    "/{template_name}/render"
)
def render_template(
    template_name: str,
    payload: dict
):
    template = resolve_template(
        template_name
    )

    if template is None:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    service_name = payload.get(
        "name"
    )

    owner = payload.get(
        "owner"
    )

    repository = payload.get(
        "repository"
    )

    environment = payload.get(
        "environment",
        "development"
    )

    if not service_name or not owner:
        raise HTTPException(
            status_code=422,
            detail="name and owner are required"
        )

    files = {
        "README.md": (
            f"# {service_name}\n\n"
            f"Owner: {owner}\n\n"
            f"Environment: {environment}\n"
        ),
        "service.yaml": (
            f"name: {service_name}\n"
            f"owner: {owner}\n"
            f"repository: {repository or ''}\n"
            f"environment: {environment}\n"
            f"template: {template_name}\n"
            f"template_version: {template.version}\n"
        )
    }

    if template_name == "backend-service":
        files["app/main.py"] = (
            "from fastapi import FastAPI\n\n"
            "app = FastAPI()\n\n"
            "@app.get('/health')\n"
            "def health():\n"
            "    return {'status': 'ok'}\n"
        )

        files["requirements.txt"] = (
            "fastapi\n"
            "uvicorn\n"
        )

    elif template_name == "worker-service":
        files["worker.py"] = (
            "def run():\n"
            "    return 'worker-ready'\n\n"
            "if __name__ == '__main__':\n"
            "    run()\n"
        )

    elif template_name == "scheduled-job":
        files["job.py"] = (
            "def run():\n"
            "    return 'job-completed'\n\n"
            "if __name__ == '__main__':\n"
            "    run()\n"
        )

    return {
        "template": template.name,
        "version": template.version,
        "type": template.type,
        "service": service_name,
        "files": files
    }