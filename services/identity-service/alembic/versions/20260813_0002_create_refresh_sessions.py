"""create refresh sessions

Revision ID: identity_0002
Revises: identity_0001
Create Date: 2026-08-13
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "identity_0002"

down_revision: Union[
    str,
    Sequence[str],
    None
] = "identity_0001"

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
        "refresh_sessions",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "token_id",
            sa.String(
                length=64
            ),
            nullable=False
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False
        ),
        sa.Column(
            "revoked",
            sa.Boolean(),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            [
                "user_id"
            ],
            [
                "platform_users.id"
            ],
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
        sa.UniqueConstraint(
            "token_id"
        )
    )

    op.create_index(
        "ix_refresh_sessions_id",
        "refresh_sessions",
        [
            "id"
        ],
        unique=False
    )

    op.create_index(
        "ix_refresh_sessions_token_id",
        "refresh_sessions",
        [
            "token_id"
        ],
        unique=True
    )

    op.create_index(
        "ix_refresh_sessions_user_id",
        "refresh_sessions",
        [
            "user_id"
        ],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_refresh_sessions_user_id",
        table_name="refresh_sessions"
    )

    op.drop_index(
        "ix_refresh_sessions_token_id",
        table_name="refresh_sessions"
    )

    op.drop_index(
        "ix_refresh_sessions_id",
        table_name="refresh_sessions"
    )

    op.drop_table(
        "refresh_sessions"
    )
