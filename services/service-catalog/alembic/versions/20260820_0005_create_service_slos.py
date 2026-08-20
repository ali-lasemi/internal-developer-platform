"""create service slos

Revision ID: catalog_0005
Revises: catalog_0004
Create Date: 2026-08-20
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "catalog_0005"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "catalog_0004"

branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_slos",
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
            "name",
            sa.String(
                length=255
            ),
            nullable=False
        ),
        sa.Column(
            "objective_type",
            sa.String(
                length=50
            ),
            nullable=False
        ),
        sa.Column(
            "target",
            sa.Float(),
            nullable=False
        ),
        sa.Column(
            "window_days",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "latency_threshold_ms",
            sa.Integer(),
            nullable=True
        ),
        sa.Column(
            "description",
            sa.String(
                length=1000
            ),
            nullable=True
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        ),
        sa.Column(
            "observed_percentage",
            sa.Float(),
            nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False
        ),
        sa.Column(
            "updated_at",
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
        ),
        sa.UniqueConstraint(
            "service_id",
            "name",
            name=(
                "uq_service_slos_"
                "service_name"
            )
        )
    )

    op.create_index(
        "ix_service_slos_service_id",
        "service_slos",
        [
            "service_id"
        ],
        unique=False
    )

    op.create_index(
        "ix_service_slos_objective_type",
        "service_slos",
        [
            "objective_type"
        ],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_service_slos_objective_type",
        table_name="service_slos"
    )

    op.drop_index(
        "ix_service_slos_service_id",
        table_name="service_slos"
    )

    op.drop_table(
        "service_slos"
    )