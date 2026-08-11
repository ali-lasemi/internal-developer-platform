from fastapi import APIRouter
from app.models.template import Template

router = APIRouter(
    prefix="/templates",
    tags=["templates"]
)


templates = []


@router.get("")
def list_templates():
    return templates


@router.post("")
def register_template(template: Template):
    templates.append(template)
    return template
