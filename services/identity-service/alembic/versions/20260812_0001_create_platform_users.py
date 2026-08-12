"""create platform users

Revision ID: identity_0001
Revises:
Create Date: 2026-08-12
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "identity_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_users",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "username",
            sa.String(length=100),
            nullable=False
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False
        ),
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False
        ),
        sa.Column(
            "team",
            sa.String(length=100),
            nullable=False
        ),
        sa.Column(
            "role",
            sa.String(length=50),
            nullable=False
        ),
        sa.Column(
            "active",
            sa.Boolean(),
            nullable=False
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
        sa.UniqueConstraint(
            "email"
        ),
        sa.UniqueConstraint(
            "username"
        )
    )

    op.create_index(
        "ix_platform_users_id",
        "platform_users",
        [
            "id"
        ],
        unique=False
    )

    op.create_index(
        "ix_platform_users_username",
        "platform_users",
        [
            "username"
        ],
        unique=True
    )

    op.create_index(
        "ix_platform_users_email",
        "platform_users",
        [
            "email"
        ],
        unique=True
    )

    op.create_index(
        "ix_platform_users_team",
        "platform_users",
        [
            "team"
        ],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_platform_users_team",
        table_name="platform_users"
    )

    op.drop_index(
        "ix_platform_users_email",
        table_name="platform_users"
    )

    op.drop_index(
        "ix_platform_users_username",
        table_name="platform_users"
    )

    op.drop_index(
        "ix_platform_users_id",
        table_name="platform_users"
    )

    op.drop_table(
        "platform_users"
    )
