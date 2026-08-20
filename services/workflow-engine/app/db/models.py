from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Text

from app.db.database import Base


class WorkflowExecutionRecord(Base):
    __tablename__ = "workflow_executions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    execution_id = Column(
        String(64),
        nullable=False,
        unique=True,
        index=True
    )

    workflow = Column(
        String(150),
        nullable=False,
        index=True
    )

    status = Column(
        String(50),
        nullable=False,
        index=True
    )

    attempt = Column(
        Integer,
        nullable=False,
        default=1
    )

    parent_execution_id = Column(
        String(64),
        nullable=True,
        index=True
    )

    service_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    service_name = Column(
        String(150),
        nullable=True,
        index=True
    )

    owner = Column(
        String(150),
        nullable=True,
        index=True
    )

    steps = Column(
        JSON,
        nullable=False
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=False
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    failed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    error = Column(
        Text,
        nullable=True
    )