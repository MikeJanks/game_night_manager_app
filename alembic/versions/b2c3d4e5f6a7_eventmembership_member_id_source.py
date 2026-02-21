"""eventmembership member_id source refactor

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create membersource enum
    membersource_enum = postgresql.ENUM("app_user", "discord", name="membersource", create_type=True)
    membersource_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add member_id and source columns (nullable initially)
    op.add_column("eventmembership", sa.Column("member_id", sa.String(), nullable=True))
    op.add_column(
        "eventmembership",
        sa.Column("source", postgresql.ENUM("app_user", "discord", name="membersource", create_type=False), nullable=True),
    )

    # 3. Backfill from user_id
    op.execute(
        "UPDATE eventmembership SET member_id = user_id::text, source = 'app_user' WHERE user_id IS NOT NULL"
    )

    # 4. Backfill from external_source/external_id
    op.execute(
        "UPDATE eventmembership SET member_id = external_id, source = 'discord' WHERE external_source = 'discord'"
    )

    # 5. Alter to NOT NULL
    op.alter_column(
        "eventmembership",
        "member_id",
        existing_type=sa.String(),
        nullable=False,
    )
    op.alter_column(
        "eventmembership",
        "source",
        existing_type=postgresql.ENUM("app_user", "discord", name="membersource", create_type=False),
        nullable=False,
    )

    # 6. Drop FK and old columns
    op.drop_constraint("eventmembership_user_id_fkey", "eventmembership", type_="foreignkey")
    op.drop_column("eventmembership", "user_id")
    op.drop_column("eventmembership", "external_source")
    op.drop_column("eventmembership", "external_id")
    op.drop_column("eventmembership", "display_name")

    # 7. Add unique constraint
    op.create_unique_constraint(
        "uq_event_member_source",
        "eventmembership",
        ["event_id", "member_id", "source"],
    )

    # 8. Drop externalsource enum
    postgresql.ENUM(name="externalsource").drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    # Recreate externalsource enum
    externalsource_enum = postgresql.ENUM("discord", name="externalsource", create_type=True)
    externalsource_enum.create(op.get_bind(), checkfirst=True)

    # Drop unique constraint
    op.drop_constraint("uq_event_member_source", "eventmembership", type_="unique")

    # Add old columns back
    op.add_column("eventmembership", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column(
        "eventmembership",
        sa.Column(
            "external_source",
            postgresql.ENUM("discord", name="externalsource", create_type=False),
            nullable=True,
        ),
    )
    op.add_column("eventmembership", sa.Column("external_id", sa.String(), nullable=True))
    op.add_column("eventmembership", sa.Column("display_name", sa.String(), nullable=True))

    # Backfill from member_id/source (lossy: we lose app_user vs discord distinction for downgrade)
    op.execute(
        "UPDATE eventmembership SET user_id = member_id::uuid, external_source = NULL, external_id = NULL "
        "WHERE source = 'app_user'"
    )
    op.execute(
        "UPDATE eventmembership SET user_id = NULL, external_source = 'discord', external_id = member_id "
        "WHERE source = 'discord'"
    )

    # Drop member_id and source
    op.drop_column("eventmembership", "member_id")
    op.drop_column("eventmembership", "source")

    # Recreate FK
    op.create_foreign_key(
        "eventmembership_user_id_fkey",
        "eventmembership",
        "user",
        ["user_id"],
        ["id"],
    )

    # Drop membersource enum
    postgresql.ENUM(name="membersource").drop(op.get_bind(), checkfirst=True)
