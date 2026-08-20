"""add workflow service context

Revision ID: workflow_0004
Revises: workflow_0003
"""

from alembic import op
import sqlalchemy as sa


revision = "workflow_0004"
down_revision = "workflow_0003"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "workflow_executions",
        sa.Column(
            "service_id",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "workflow_executions",
        sa.Column(
            "service_name",
            sa.String(length=150),
            nullable=True
        )
    )

    op.add_column(
        "workflow_executions",
        sa.Column(
            "owner",
            sa.String(length=150),
            nullable=True
        )
    )

    op.create_index(
        "ix_workflow_executions_service_id",
        "workflow_executions",
        ["service_id"],
        unique=False
    )

    op.create_index(
        "ix_workflow_executions_service_name",
        "workflow_executions",
        ["service_name"],
        unique=False
    )

    op.create_index(
        "ix_workflow_executions_owner",
        "workflow_executions",
        ["owner"],
        unique=False
    )


def downgrade():
    op.drop_index(
        "ix_workflow_executions_owner",
        table_name="workflow_executions"
    )

    op.drop_index(
        "ix_workflow_executions_service_name",
        table_name="workflow_executions"
    )

    op.drop_index(
        "ix_workflow_executions_service_id",
        table_name="workflow_executions"
    )

    op.drop_column(
        "workflow_executions",
        "owner"
    )

    op.drop_column(
        "workflow_executions",
        "service_name"
    )

    op.drop_column(
        "workflow_executions",
        "service_id"
    )