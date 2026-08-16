"""create transactional outbox

Revision ID: catalog_0003
Revises: catalog_0002
Create Date: 2026-08-16
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "catalog_0003"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "catalog_0002"

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
        "service_catalog_outbox",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "event_id",
            sa.String(
                length=64
            ),
            nullable=False
        ),
        sa.Column(
            "event_type",
            sa.String(
                length=150
            ),
            nullable=False
        ),
        sa.Column(
            "source",
            sa.String(
                length=150
            ),
            nullable=False
        ),
        sa.Column(
            "subject",
            sa.String(
                length=255
            ),
            nullable=False
        ),
        sa.Column(
            "payload",
            sa.JSON(),
            nullable=False
        ),
        sa.Column(
            "status",
            sa.String(
                length=30
            ),
            nullable=False,
            server_default="pending"
        ),
        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
            server_default="0"
        ),
        sa.Column(
            "last_error",
            sa.Text(),
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
            "published_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
        sa.UniqueConstraint(
            "event_id"
        )
    )

    op.create_index(
        "ix_service_catalog_outbox_event_id",
        "service_catalog_outbox",
        [
            "event_id"
        ],
        unique=True
    )

    op.create_index(
        "ix_service_catalog_outbox_event_type",
        "service_catalog_outbox",
        [
            "event_type"
        ],
        unique=False
    )

    op.create_index(
        "ix_service_catalog_outbox_subject",
        "service_catalog_outbox",
        [
            "subject"
        ],
        unique=False
    )

    op.create_index(
        "ix_service_catalog_outbox_status",
        "service_catalog_outbox",
        [
            "status"
        ],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_service_catalog_outbox_status",
        table_name="service_catalog_outbox"
    )

    op.drop_index(
        "ix_service_catalog_outbox_subject",
        table_name="service_catalog_outbox"
    )

    op.drop_index(
        "ix_service_catalog_outbox_event_type",
        table_name="service_catalog_outbox"
    )

    op.drop_index(
        "ix_service_catalog_outbox_event_id",
        table_name="service_catalog_outbox"
    )

    op.drop_table(
        "service_catalog_outbox"
    )