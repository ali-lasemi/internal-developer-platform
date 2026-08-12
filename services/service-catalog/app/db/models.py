from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from app.db.database import Base


class ServiceRecord(Base):
    __tablename__ = "services"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    owner = Column(
        String(100),
        nullable=False,
        index=True
    )

    repository = Column(
        String(500),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    lifecycle = Column(
        String(50),
        nullable=False,
        default="created"
    )
