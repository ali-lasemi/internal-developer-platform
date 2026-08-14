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
