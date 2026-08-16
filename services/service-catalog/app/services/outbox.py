import os
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from uuid import uuid4

import httpx
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models import OutboxEventRecord


EVENT_PLATFORM_URL = os.getenv(
    "EVENT_PLATFORM_URL",
    "http://event-platform:8000"
)

OUTBOX_MAX_ATTEMPTS = int(
    os.getenv(
        "OUTBOX_MAX_ATTEMPTS",
        "5"
    )
)

OUTBOX_BASE_RETRY_SECONDS = int(
    os.getenv(
        "OUTBOX_BASE_RETRY_SECONDS",
        "2"
    )
)

OUTBOX_MAX_RETRY_SECONDS = int(
    os.getenv(
        "OUTBOX_MAX_RETRY_SECONDS",
        "300"
    )
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
        attempts=0,
        next_attempt_at=None
    )

    database.add(
        record
    )

    return record


def retry_delay_seconds(
    attempts: int
) -> int:
    exponent = max(
        attempts - 1,
        0
    )

    delay = (
        OUTBOX_BASE_RETRY_SECONDS
        * (
            2 ** exponent
        )
    )

    return min(
        delay,
        OUTBOX_MAX_RETRY_SECONDS
    )


async def dispatch_outbox_record(
    database: Session,
    record: OutboxEventRecord
) -> bool:
    if record.status == "published":
        return True

    if record.status == "dead_letter":
        return False

    now = datetime.now(
        timezone.utc
    )

    if (
        record.next_attempt_at
        and record.next_attempt_at > now
    ):
        return False

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

        record.published_at = now
        record.next_attempt_at = None
        record.dead_lettered_at = None
        record.last_error = None

        database.commit()

        return True

    except Exception as exc:
        record.last_error = str(
            exc
        )

        if (
            record.attempts
            >= OUTBOX_MAX_ATTEMPTS
        ):
            record.status = (
                "dead_letter"
            )

            record.dead_lettered_at = now
            record.next_attempt_at = None

        else:
            record.status = "pending"

            record.next_attempt_at = (
                now
                + timedelta(
                    seconds=retry_delay_seconds(
                        record.attempts
                    )
                )
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

    now = datetime.now(
        timezone.utc
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
        .filter(
            or_(
                OutboxEventRecord.next_attempt_at
                .is_(None),
                OutboxEventRecord.next_attempt_at
                <= now
            )
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


def redrive_dead_letters(
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
            == "dead_letter"
        )
        .order_by(
            OutboxEventRecord.id.asc()
        )
        .limit(
            safe_limit
        )
        .all()
    )

    for record in records:
        record.status = "pending"
        record.attempts = 0
        record.last_error = None
        record.dead_lettered_at = None
        record.next_attempt_at = None

    database.commit()

    return {
        "redriven": len(
            records
        )
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