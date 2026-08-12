from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import ServiceRecord
from app.models.catalog import CatalogService
from app.models.catalog import CatalogServiceCreate


router = APIRouter(
    prefix="/catalog",
    tags=["catalog"]
)


@router.get(
    "",
    response_model=list[CatalogService]
)
def list_catalog(
    database: Session = Depends(get_db)
):
    return (
        database
        .query(ServiceRecord)
        .order_by(ServiceRecord.id.asc())
        .all()
    )


@router.get(
    "/{service_id}",
    response_model=CatalogService
)
def get_service(
    service_id: int,
    database: Session = Depends(get_db)
):
    service = (
        database
        .query(ServiceRecord)
        .filter(ServiceRecord.id == service_id)
        .first()
    )

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service


@router.post(
    "",
    response_model=CatalogService,
    status_code=201
)
def register_service(
    service: CatalogServiceCreate,
    database: Session = Depends(get_db)
):
    existing = (
        database
        .query(ServiceRecord)
        .filter(ServiceRecord.name == service.name)
        .first()
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Service already exists"
        )

    record = ServiceRecord(
        name=service.name,
        owner=service.owner,
        repository=service.repository,
        description=service.description,
        lifecycle=service.lifecycle
    )

    database.add(record)
    database.commit()
    database.refresh(record)

    return record
