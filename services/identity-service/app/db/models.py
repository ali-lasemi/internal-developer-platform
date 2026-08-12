from datetime import datetime
from datetime import timezone

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from app.db.database import Base


class UserRecord(Base):
    __tablename__ = "platform_users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    team = Column(
        String(100),
        nullable=False,
        index=True
    )

    role = Column(
        String(50),
        nullable=False,
        default="developer"
    )

    active = Column(
        Boolean,
        nullable=False,
        default=True
    )


class RefreshSessionRecord(Base):
    __tablename__ = "refresh_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    token_id = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey(
            "platform_users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    revoked = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(
            timezone.utc
        )
    )
