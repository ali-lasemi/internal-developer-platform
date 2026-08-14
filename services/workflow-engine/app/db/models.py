from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import JSON
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

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