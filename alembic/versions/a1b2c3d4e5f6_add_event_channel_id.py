"""add event channel_id

Revision ID: a1b2c3d4e5f6
Revises: 58e1cf0af97a
Create Date: 2026-02-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "58e1cf0af97a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "event",
        sa.Column("channel_id", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("event", "channel_id")
