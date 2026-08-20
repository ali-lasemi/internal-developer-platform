from datetime import datetime
from datetime import timezone

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import ServiceRecord
from app.db.models import ServiceSLORecord
from app.models.slo import ErrorBudgetResponse
from app.models.slo import OBJECTIVE_TYPES
from app.models.slo import SLOCreate
from app.models.slo import SLOResponse
from app.models.slo import SLOSummaryResponse
from app.models.slo import SLOUpdate
from app.services.outbox import create_outbox_event
from app.services.outbox import dispatch_outbox_record
from app.services.reliability import calculate_error_budget
from app.services.reliability import summarize_slos


router = APIRouter(
    prefix="/catalog",
    tags=["slos"]
)


def require_service(
    service_id: int,
    database: Session
) -> ServiceRecord:
    service = (
        database
        .query(
            ServiceRecord
        )
        .filter(
            ServiceRecord.id
            == service_id
        )
        .first()
    )

    if service is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return service


def require_slo(
    service_id: int,
    slo_id: int,
    database: Session
) -> ServiceSLORecord:
    slo = (
        database
        .query(
            ServiceSLORecord
        )
        .filter(
            ServiceSLORecord.id
            == slo_id
        )
        .filter(
            ServiceSLORecord.service_id
            == service_id
        )
        .first()
    )

    if slo is None:
        raise HTTPException(
            status_code=404,
            detail="SLO not found"
        )

    return slo


@router.post(
    "/{service_id}/slos",
    response_model=SLOResponse,
    status_code=201
)
async def create_slo(
    service_id: int,
    request: SLOCreate,
    database: Session = Depends(
        get_db
    )
):
    service = require_service(
        service_id,
        database
    )

    record = ServiceSLORecord(
        service_id=service_id,
        **request.model_dump()
    )

    database.add(
        record
    )

    event = create_outbox_event(
        database=database,
        event_type="slo.created",
        subject=service.name,
        payload={
            "service_id": service_id,
            "name": request.name,
            "objective_type": (
                request.objective_type
            ),
            "target": request.target,
            "window_days": (
                request.window_days
            )
        }
    )

    try:
        database.commit()

    except IntegrityError as exc:
        database.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "SLO name already exists "
                "for this service"
            )
        ) from exc

    database.refresh(
        record
    )

    database.refresh(
        event
    )

    await dispatch_outbox_record(
        database,
        event
    )

    return record


@router.get(
    "/{service_id}/slos",
    response_model=list[SLOResponse]
)
def list_slos(
    service_id: int,
    database: Session = Depends(
        get_db
    )
):
    require_service(
        service_id,
        database
    )

    return (
        database
        .query(
            ServiceSLORecord
        )
        .filter(
            ServiceSLORecord.service_id
            == service_id
        )
        .order_by(
            ServiceSLORecord.id.asc()
        )
        .all()
    )


@router.get(
    "/{service_id}/slos/{slo_id}",
    response_model=SLOResponse
)
def get_slo(
    service_id: int,
    slo_id: int,
    database: Session = Depends(
        get_db
    )
):
    require_service(
        service_id,
        database
    )

    return require_slo(
        service_id,
        slo_id,
        database
    )


@router.patch(
    "/{service_id}/slos/{slo_id}",
    response_model=SLOResponse
)
async def update_slo(
    service_id: int,
    slo_id: int,
    request: SLOUpdate,
    database: Session = Depends(
        get_db
    )
):
    service = require_service(
        service_id,
        database
    )

    record = require_slo(
        service_id,
        slo_id,
        database
    )

    updates = request.model_dump(
        exclude_unset=True
    )

    objective_type = updates.get(
        "objective_type",
        record.objective_type
    )

    latency_threshold = updates.get(
        "latency_threshold_ms",
        record.latency_threshold_ms
    )

    if (
        objective_type
        not in OBJECTIVE_TYPES
    ):
        raise HTTPException(
            status_code=422,
            detail="Unsupported objective_type"
        )

    if (
        objective_type == "latency"
        and latency_threshold is None
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "latency_threshold_ms "
                "is required for latency SLO"
            )
        )

    for field, value in updates.items():
        setattr(
            record,
            field,
            value
        )

    record.updated_at = datetime.now(
        timezone.utc
    )

    event = create_outbox_event(
        database=database,
        event_type="slo.updated",
        subject=service.name,
        payload={
            "service_id": service_id,
            "slo_id": slo_id,
            "changes": updates
        }
    )

    try:
        database.commit()

    except IntegrityError as exc:
        database.rollback()

        raise HTTPException(
            status_code=409,
            detail=(
                "SLO name already exists "
                "for this service"
            )
        ) from exc

    database.refresh(
        record
    )

    database.refresh(
        event
    )

    await dispatch_outbox_record(
        database,
        event
    )

    return record


@router.delete(
    "/{service_id}/slos/{slo_id}",
    status_code=204
)
async def delete_slo(
    service_id: int,
    slo_id: int,
    database: Session = Depends(
        get_db
    )
):
    service = require_service(
        service_id,
        database
    )

    record = require_slo(
        service_id,
        slo_id,
        database
    )

    payload = {
        "service_id": service_id,
        "slo_id": record.id,
        "name": record.name,
        "objective_type": (
            record.objective_type
        )
    }

    database.delete(
        record
    )

    event = create_outbox_event(
        database=database,
        event_type="slo.deleted",
        subject=service.name,
        payload=payload
    )

    database.commit()

    database.refresh(
        event
    )

    await dispatch_outbox_record(
        database,
        event
    )

    return Response(
        status_code=204
    )


@router.get(
    "/{service_id}/slos/{slo_id}/error-budget",
    response_model=ErrorBudgetResponse
)
def error_budget(
    service_id: int,
    slo_id: int,
    database: Session = Depends(
        get_db
    )
):
    require_service(
        service_id,
        database
    )

    record = require_slo(
        service_id,
        slo_id,
        database
    )

    budget = calculate_error_budget(
        target=record.target,
        window_days=record.window_days,
        observed_percentage=(
            record.observed_percentage
        )
    )

    return {
        "slo_id": record.id,
        "service_id": service_id,
        **budget
    }


@router.get(
    "/{service_id}/slo-summary",
    response_model=SLOSummaryResponse
)
def slo_summary(
    service_id: int,
    database: Session = Depends(
        get_db
    )
):
    require_service(
        service_id,
        database
    )

    records = (
        database
        .query(
            ServiceSLORecord
        )
        .filter(
            ServiceSLORecord.service_id
            == service_id
        )
        .order_by(
            ServiceSLORecord.id.asc()
        )
        .all()
    )

    return summarize_slos(
        service_id,
        records
    )


@router.get(
    "/slo/metrics"
)
def slo_metrics(
    database: Session = Depends(
        get_db
    )
):
    records = (
        database
        .query(
            ServiceSLORecord
        )
        .all()
    )

    services_with_slos = len(
        {
            record.service_id
            for record in records
            if record.enabled
        }
    )

    healthy = 0
    warning = 0
    exhausted = 0
    unknown = 0

    for record in records:
        if not record.enabled:
            continue

        budget = calculate_error_budget(
            target=record.target,
            window_days=record.window_days,
            observed_percentage=(
                record.observed_percentage
            )
        )

        status = budget[
            "status"
        ]

        if status == "healthy":
            healthy += 1

        elif status == "warning":
            warning += 1

        elif status == "exhausted":
            exhausted += 1

        else:
            unknown += 1

    return {
        "services_with_slos": (
            services_with_slos
        ),
        "total_slos": len(
            records
        ),
        "enabled_slos": sum(
            1
            for record in records
            if record.enabled
        ),
        "healthy_slos": healthy,
        "warning_slos": warning,
        "exhausted_slos": exhausted,
        "unknown_slos": unknown
    }