import os
from datetime import datetime
from datetime import timezone
from uuid import uuid4

import httpx
from sqlalchemy.orm import Session

from app.db.models import OutboxEventRecord


EVENT_PLATFORM_URL = os.getenv(
    "EVENT_PLATFORM_URL",
    "http://event-platform:8000"
)


def create_outbox_event(
    database: Session,
    event_type: str,
    subject: str,
    payload: dict
) -> OutboxEventRecord:
    record = OutboxEventRecord(
        event_id=uuid4().hex,
        event_type=event_type,
        source="service-catalog",
        subject=subject,
        payload=payload,
        status="pending",
        attempts=0
    )

    database.add(
        record
    )

    return record


async def dispatch_outbox_record(
    database: Session,
    record: OutboxEventRecord
) -> bool:
    if record.status == "published":
        return True

    record.attempts += 1

    try:
        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:
            response = await client.post(
                f"{EVENT_PLATFORM_URL}/events",
                json={
                    "id": record.event_id,
                    "type": record.event_type,
                    "source": record.source,
                    "subject": record.subject,
                    "data": record.payload
                }
            )

            response.raise_for_status()

        record.status = "published"
        record.published_at = datetime.now(
            timezone.utc
        )
        record.last_error = None

        database.commit()

        return True

    except Exception as exc:
        record.status = "pending"
        record.last_error = str(
            exc
        )

        database.commit()

        return False


async def dispatch_pending_outbox(
    database: Session,
    limit: int = 100
) -> dict:
    safe_limit = min(
        max(
            limit,
            1
        ),
        500
    )

    records = (
        database
        .query(
            OutboxEventRecord
        )
        .filter(
            OutboxEventRecord.status
            == "pending"
        )
        .order_by(
            OutboxEventRecord.id.asc()
        )
        .limit(
            safe_limit
        )
        .all()
    )

    published = 0
    failed = 0

    for record in records:
        success = await dispatch_outbox_record(
            database,
            record
        )

        if success:
            published += 1
        else:
            failed += 1

    return {
        "processed": len(
            records
        ),
        "published": published,
        "failed": failed
    }


def list_outbox(
    database: Session,
    status: str | None = None,
    limit: int = 100
):
    safe_limit = min(
        max(
            limit,
            1
        ),
        500
    )

    query = database.query(
        OutboxEventRecord
    )

    if status:
        query = query.filter(
            OutboxEventRecord.status
            == status
        )

    return (
        query
        .order_by(
            OutboxEventRecord.id.desc()
        )
        .limit(
            safe_limit
        )
        .all()
    )