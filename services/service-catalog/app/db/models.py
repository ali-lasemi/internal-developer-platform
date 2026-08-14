from datetime import datetime
from datetime import timezone

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

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