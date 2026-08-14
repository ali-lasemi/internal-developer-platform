from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import ServiceLifecycleHistoryRecord
from app.db.models import ServiceRecord
from app.events.lifecycle_events import publish_lifecycle_changed_event
from app.models.catalog import CatalogService
from app.models.catalog import CatalogServiceCreate
from app.models.history import LifecycleHistoryEntry
from app.models.lifecycle import LifecycleTransitionRequest
from app.models.lifecycle import LifecycleTransitionResponse
from app.services.lifecycle import validate_transition


router = APIRouter(
    prefix="/catalog",
    tags=["catalog"]
)


@router.get(
    "",
    response_model=list[CatalogService]
)
def list_catalog(
    owner: str | None = None,
    lifecycle: str | None = None,
    limit: int = 100,
    database: Session = Depends(
        get_db
    )
):
    query = database.query(
        ServiceRecord
    )

    if owner:
        query = query.filter(
            ServiceRecord.owner == owner
        )

    if lifecycle:
        query = query.filter(
            ServiceRecord.lifecycle
            == lifecycle
        )

    safe_limit = min(
        max(
            limit,
            1
        ),
        500
    )

    return (
        query
        .order_by(
            ServiceRecord.id.desc()
        )
        .limit(
            safe_limit
        )
        .all()
    )


@router.get(
    "/metrics"
)
def catalog_metrics(
    database: Session = Depends(
        get_db
    )
):
    total = (
        database
        .query(
            func.count(
                ServiceRecord.id
            )
        )
        .scalar()
        or 0
    )

    rows = (
        database
        .query(
            ServiceRecord.lifecycle,
            func.count(
                ServiceRecord.id
            )
        )
        .group_by(
            ServiceRecord.lifecycle
        )
        .all()
    )

    lifecycle = {
        state: count
        for state, count in rows
    }

    return {
        "total_services": total,
        "lifecycle": lifecycle,
        "production": lifecycle.get(
            "production",
            0
        ),
        "deprecated": lifecycle.get(
            "deprecated",
            0
        ),
        "retired": lifecycle.get(
            "retired",
            0
        )
    }

@router.get(
    "/owners/{owner}/summary"
)
def owner_summary(
    owner: str,
    database: Session = Depends(
        get_db
    )
):
    services = (
        database
        .query(
            ServiceRecord
        )
        .filter(
            ServiceRecord.owner == owner
        )
        .order_by(
            ServiceRecord.id.desc()
        )
        .all()
    )

    lifecycle = {}

    for service in services:
        lifecycle[
            service.lifecycle
        ] = (
            lifecycle.get(
                service.lifecycle,
                0
            )
            + 1
        )

    return {
        "owner": owner,
        "total_services": len(
            services
        ),
        "lifecycle": lifecycle,
        "services": services
    }

@router.get(
    "/{service_id}",
    response_model=CatalogService
)
def get_service(
    service_id: int,
    database: Session = Depends(
        get_db
    )
):
    service = (
        database
        .query(ServiceRecord)
        .filter(
            ServiceRecord.id == service_id
        )
        .first()
    )

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service


@router.get(
    "/{service_id}/lifecycle/history",
    response_model=list[LifecycleHistoryEntry]
)
def get_lifecycle_history(
    service_id: int,
    database: Session = Depends(
        get_db
    )
):
    service = (
        database
        .query(ServiceRecord)
        .filter(
            ServiceRecord.id == service_id
        )
        .first()
    )

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return (
        database
        .query(ServiceLifecycleHistoryRecord)
        .filter(
            ServiceLifecycleHistoryRecord.service_id
            == service_id
        )
        .order_by(
            ServiceLifecycleHistoryRecord.id.asc()
        )
        .all()
    )


@router.post(
    "",
    response_model=CatalogService,
    status_code=201
)
def register_service(
    service: CatalogServiceCreate,
    database: Session = Depends(
        get_db
    )
):
    existing = (
        database
        .query(ServiceRecord)
        .filter(
            ServiceRecord.name == service.name
        )
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

    database.add(
        record
    )

    database.commit()
    database.refresh(
        record
    )

    return record


@router.post(
    "/{service_id}/lifecycle",
    response_model=LifecycleTransitionResponse
)
async def transition_lifecycle(
    service_id: int,
    request: LifecycleTransitionRequest,
    database: Session = Depends(
        get_db
    )
):
    service = (
        database
        .query(ServiceRecord)
        .filter(
            ServiceRecord.id == service_id
        )
        .first()
    )

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    previous = service.lifecycle

    if not validate_transition(
        previous,
        request.lifecycle
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                f"Lifecycle transition from "
                f"{previous} to {request.lifecycle} "
                f"is not allowed"
            )
        )

    service.lifecycle = request.lifecycle

    history = ServiceLifecycleHistoryRecord(
        service_id=service.id,
        previous_lifecycle=previous,
        lifecycle=request.lifecycle
    )

    database.add(
        history
    )

    database.commit()
    database.refresh(
        service
    )

    try:
        await publish_lifecycle_changed_event(
            service_name=service.name,
            owner=service.owner,
            previous_lifecycle=previous,
            lifecycle=service.lifecycle
        )

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Lifecycle event publishing failed: {exc}"
        ) from exc

    return LifecycleTransitionResponse(
        id=service.id,
        name=service.name,
        previous_lifecycle=previous,
        lifecycle=service.lifecycle
    )
