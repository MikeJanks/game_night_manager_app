"""membersource enum uppercase

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-02-17

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create new enum with uppercase values
    membersource_new = postgresql.ENUM("APP_USER", "DISCORD", name="membersource_new", create_type=True)
    membersource_new.create(op.get_bind(), checkfirst=True)

    # 2. Alter column to use new enum, mapping existing values
    op.execute(
        """
        ALTER TABLE eventmembership
        ALTER COLUMN source TYPE membersource_new
        USING (
            CASE source::text
                WHEN 'app_user' THEN 'APP_USER'::membersource_new
                WHEN 'discord' THEN 'DISCORD'::membersource_new
                ELSE 'APP_USER'::membersource_new
            END
        )
        """
    )

    # 3. Drop old enum
    postgresql.ENUM(name="membersource").drop(op.get_bind(), checkfirst=True)

    # 4. Rename new enum to membersource
    op.execute("ALTER TYPE membersource_new RENAME TO membersource")


def downgrade() -> None:
    # 1. Create old enum with lowercase values
    membersource_old = postgresql.ENUM("app_user", "discord", name="membersource_old", create_type=True)
    membersource_old.create(op.get_bind(), checkfirst=True)

    # 2. Alter column to use old enum, mapping back
    op.execute(
        """
        ALTER TABLE eventmembership
        ALTER COLUMN source TYPE membersource_old
        USING (
            CASE source::text
                WHEN 'APP_USER' THEN 'app_user'::membersource_old
                WHEN 'DISCORD' THEN 'discord'::membersource_old
                ELSE 'app_user'::membersource_old
            END
        )
        """
    )

    # 3. Drop membersource (the renamed type)
    postgresql.ENUM(name="membersource").drop(op.get_bind(), checkfirst=True)

    # 4. Rename membersource_old to membersource
    op.execute("ALTER TYPE membersource_old RENAME TO membersource")
