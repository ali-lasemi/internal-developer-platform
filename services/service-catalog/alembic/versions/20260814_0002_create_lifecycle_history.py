"""create lifecycle history

Revision ID: catalog_0002
Revises: catalog_0001
Create Date: 2026-08-14
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "catalog_0002"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "catalog_0001"

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
    op.create_table(
        "service_lifecycle_history",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "service_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "previous_lifecycle",
            sa.String(
                length=50
            ),
            nullable=False
        ),
        sa.Column(
            "lifecycle",
            sa.String(
                length=50
            ),
            nullable=False
        ),
        sa.Column(
            "changed_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            [
                "service_id"
            ],
            [
                "services.id"
            ],
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint(
            "id"
        )
    )

    op.create_index(
        "ix_service_lifecycle_history_id",
        "service_lifecycle_history",
        [
            "id"
        ],
        unique=False
    )

    op.create_index(
        "ix_service_lifecycle_history_service_id",
        "service_lifecycle_history",
        [
            "service_id"
        ],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_service_lifecycle_history_service_id",
        table_name="service_lifecycle_history"
    )

    op.drop_index(
        "ix_service_lifecycle_history_id",
        table_name="service_lifecycle_history"
    )

    op.drop_table(
        "service_lifecycle_history"
    )
