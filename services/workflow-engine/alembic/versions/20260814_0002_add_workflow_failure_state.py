"""add workflow failure state

Revision ID: workflow_0002
Revises: workflow_0001
Create Date: 2026-08-14
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "workflow_0002"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "workflow_0001"

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
            "failed_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True
        )
    )

    op.add_column(
        "workflow_executions",
        sa.Column(
            "error",
            sa.Text(),
            nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column(
        "workflow_executions",
        "error"
    )

    op.drop_column(
        "workflow_executions",
        "failed_at"
    )