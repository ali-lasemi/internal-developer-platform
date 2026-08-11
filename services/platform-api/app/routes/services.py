from fastapi import APIRouter
from app.models.service import Service

router = APIRouter(
    prefix="/services",
    tags=["services"]
)


services = []


@router.get("")
def list_services():
    return services


@router.post("")
def create_service(service: Service):
    services.append(service)
    return service
