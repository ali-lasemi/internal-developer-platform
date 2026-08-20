from datetime import datetime
from datetime import timezone

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy import UniqueConstraint

from app.db.database import Base


class ServiceRecord(Base):
    __tablename__ = "services"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    owner = Column(
        String(255),
        nullable=False,
        index=True
    )

    repository = Column(
        String(500),
        nullable=False
    )

    description = Column(
        String(1000),
        nullable=False
    )

    lifecycle = Column(
        String(50),
        nullable=False,
        default="created"
    )


class ServiceLifecycleHistoryRecord(Base):
    __tablename__ = "service_lifecycle_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    service_id = Column(
        Integer,
        ForeignKey(
            "services.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    previous_lifecycle = Column(
        String(50),
        nullable=False
    )

    lifecycle = Column(
        String(50),
        nullable=False
    )

    changed_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        )
    )

class OutboxEventRecord(Base):
    __tablename__ = "service_catalog_outbox"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    event_id = Column(
        String(64),
        nullable=False,
        unique=True,
        index=True
    )

    event_type = Column(
        String(150),
        nullable=False,
        index=True
    )

    source = Column(
        String(150),
        nullable=False
    )

    subject = Column(
        String(255),
        nullable=False,
        index=True
    )

    payload = Column(
        JSON,
        nullable=False
    )

    status = Column(
        String(30),
        nullable=False,
        default="pending",
        index=True
    )

    attempts = Column(
        Integer,
        nullable=False,
        default=0
    )

    last_error = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        )
    )

    published_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    next_attempt_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )

    dead_lettered_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

class ServiceSLORecord(Base):
    __tablename__ = "service_slos"

    __table_args__ = (
        UniqueConstraint(
            "service_id",
            "name",
            name="uq_service_slos_service_name"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    service_id = Column(
        Integer,
        ForeignKey(
            "services.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    objective_type = Column(
        String(50),
        nullable=False,
        index=True
    )

    target = Column(
        Float,
        nullable=False
    )

    window_days = Column(
        Integer,
        nullable=False
    )

    latency_threshold_ms = Column(
        Integer,
        nullable=True
    )

    description = Column(
        String(1000),
        nullable=True
    )

    enabled = Column(
        Boolean,
        nullable=False,
        default=True
    )

    observed_percentage = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        )
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        ),
        onupdate=lambda: datetime.now(
            timezone.utc
        )
    )