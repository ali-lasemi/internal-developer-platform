"""add workflow retry lineage

Revision ID: workflow_0003
Revises: workflow_0002
Create Date: 2026-08-14
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "workflow_0003"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "workflow_0002"

branch_labels: Union[
    str,
    Sequence[str],
    None
] = None

depends_on: Union[
    str,
    Sequence[str],
    None
] = None


def upgrade() -> None:
    op.add_column(
        "workflow_executions",
        sa.Column(
            "attempt",
            sa.Integer(),
            nullable=False,
            server_default="1"
        )
    )

    op.add_column(
        "workflow_executions",
        sa.Column(
            "parent_execution_id",
            sa.String(
                length=64
            ),
            nullable=True
        )
    )

    op.create_index(
        "ix_workflow_executions_parent_execution_id",
        "workflow_executions",
        [
            "parent_execution_id"
        ],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_workflow_executions_parent_execution_id",
        table_name="workflow_executions"
    )

    op.drop_column(
        "workflow_executions",
        "parent_execution_id"
    )

    op.drop_column(
        "workflow_executions",
        "attempt"
    )