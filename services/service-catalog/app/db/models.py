from datetime import datetime
from datetime import timezone

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from app.db.database import Base


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
