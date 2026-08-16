"""add outbox retry policy

Revision ID: catalog_0004
Revises: catalog_0003
Create Date: 2026-08-16
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "catalog_0004"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "catalog_0003"

branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "service_catalog_outbox",
        sa.Column(
            "next_attempt_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True
        )
    )

    op.add_column(
        "service_catalog_outbox",
        sa.Column(
            "dead_lettered_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True
        )
    )

    op.create_index(
        "ix_service_catalog_outbox_next_attempt_at",
        "service_catalog_outbox",
        [
            "next_attempt_at"
        ],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_service_catalog_outbox_next_attempt_at",
        table_name="service_catalog_outbox"
    )

    op.drop_column(
        "service_catalog_outbox",
        "dead_lettered_at"
    )

    op.drop_column(
        "service_catalog_outbox",
        "next_attempt_at"
    )