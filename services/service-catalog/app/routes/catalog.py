from fastapi import APIRouter
from app.models.catalog import CatalogService

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"]
)


catalog = []


@router.get("")
def list_catalog():
    return catalog


@router.post("")
def register_service(service: CatalogService):
    catalog.append(service)
    return service
