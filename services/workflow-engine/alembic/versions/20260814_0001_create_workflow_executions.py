"""create workflow executions

Revision ID: workflow_0001
Revises:
Create Date: 2026-08-14
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "workflow_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workflow_executions",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "execution_id",
            sa.String(length=64),
            nullable=False
        ),
        sa.Column(
            "workflow",
            sa.String(length=150),
            nullable=False
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False
        ),
        sa.Column(
            "steps",
            sa.JSON(),
            nullable=False
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
        sa.UniqueConstraint(
            "execution_id"
        )
    )

    op.create_index(
        "ix_workflow_executions_execution_id",
        "workflow_executions",
        [
            "execution_id"
        ],
        unique=True
    )

    op.create_index(
        "ix_workflow_executions_workflow",
        "workflow_executions",
        [
            "workflow"
        ],
        unique=False
    )

    op.create_index(
        "ix_workflow_executions_status",
        "workflow_executions",
        [
            "status"
        ],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_workflow_executions_status",
        table_name="workflow_executions"
    )

    op.drop_index(
        "ix_workflow_executions_workflow",
        table_name="workflow_executions"
    )

    op.drop_index(
        "ix_workflow_executions_execution_id",
        table_name="workflow_executions"
    )

    op.drop_table(
        "workflow_executions"
    )