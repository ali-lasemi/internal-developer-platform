"""create service catalog

Revision ID: catalog_0001
Revises:
Create Date: 2026-08-12
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "catalog_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False
        ),
        sa.Column(
            "owner",
            sa.String(length=100),
            nullable=False
        ),
        sa.Column(
            "repository",
            sa.String(length=500),
            nullable=False
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False
        ),
        sa.Column(
            "lifecycle",
            sa.String(length=50),
            nullable=False
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
        sa.UniqueConstraint(
            "name"
        )
    )

    op.create_index(
        "ix_services_id",
        "services",
        [
            "id"
        ],
        unique=False
    )

    op.create_index(
        "ix_services_name",
        "services",
        [
            "name"
        ],
        unique=True
    )

    op.create_index(
        "ix_services_owner",
        "services",
        [
            "owner"
        ],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_services_owner",
        table_name="services"
    )

    op.drop_index(
        "ix_services_name",
        table_name="services"
    )

    op.drop_index(
        "ix_services_id",
        table_name="services"
    )

    op.drop_table(
        "services"
    )
