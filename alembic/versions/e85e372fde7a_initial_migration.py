"""initial migration

Revision ID: e85e372fde7a
Revises: 
Create Date: 2026-01-12 02:41:33.063176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e85e372fde7a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types
    eventstatus_enum = postgresql.ENUM('PLANNING', 'CONFIRMED', 'CANCELLED', name='eventstatus', create_type=True)
    eventstatus_enum.create(op.get_bind(), checkfirst=True)
    
    membershiprole_enum = postgresql.ENUM('HOST', 'ATTENDEE', name='membershiprole', create_type=True)
    membershiprole_enum.create(op.get_bind(), checkfirst=True)
    
    membershipstatus_enum = postgresql.ENUM('PENDING', 'ACCEPTED', name='membershipstatus', create_type=True)
    membershipstatus_enum.create(op.get_bind(), checkfirst=True)
    
    messagetype_enum = postgresql.ENUM('USER', 'SYSTEM', name='messagetype', create_type=True)
    messagetype_enum.create(op.get_bind(), checkfirst=True)
    
    friendshipstatus_enum = postgresql.ENUM('PENDING', 'ACCEPTED', name='friendshipstatus', create_type=True)
    friendshipstatus_enum.create(op.get_bind(), checkfirst=True)
    
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('username', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Create game table
    op.create_table(
        'game',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('player_count', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create event table
    op.create_table(
        'event',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('game_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_name', sa.String(), nullable=False),
        sa.Column('event_datetime', sa.DateTime(), nullable=True),
        sa.Column('location_or_link', sa.String(), nullable=True),
        sa.Column('status', postgresql.ENUM('PLANNING', 'CONFIRMED', 'CANCELLED', name='eventstatus', create_type=False), nullable=False),
        sa.Column('plan_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('plan_updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['game_id'], ['game.id'], name='event_game_id_fkey')
    )
    
    # Create friendship table
    op.create_table(
        'friendship',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('friend_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'ACCEPTED', name='friendshipstatus', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('responded_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('user_id', 'friend_user_id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE', name='friendship_user_id_fkey'),
        sa.ForeignKeyConstraint(['friend_user_id'], ['user.id'], ondelete='CASCADE', name='friendship_friend_user_id_fkey')
    )
    
    # Create eventmembership table
    op.create_table(
        'eventmembership',
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', postgresql.ENUM('HOST', 'ATTENDEE', name='membershiprole', create_type=False), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'ACCEPTED', name='membershipstatus', create_type=False), nullable=False),
        sa.Column('confirmed_plan_version', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('event_id', 'user_id'),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], ondelete='CASCADE', name='eventmembership_event_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='eventmembership_user_id_fkey')
    )
    
    # Create eventmessage table
    op.create_table(
        'eventmessage',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('message_type', postgresql.ENUM('USER', 'SYSTEM', name='messagetype', create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['event.id'], ondelete='CASCADE', name='eventmessage_event_id_fkey'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='eventmessage_user_id_fkey')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('eventmessage')
    op.drop_table('eventmembership')
    op.drop_table('friendship')
    op.drop_table('event')
    op.drop_table('game')
    op.drop_table('user')
    
    # Drop ENUM types
    op.execute("DROP TYPE IF EXISTS friendshipstatus")
    op.execute("DROP TYPE IF EXISTS messagetype")
    op.execute("DROP TYPE IF EXISTS membershipstatus")
    op.execute("DROP TYPE IF EXISTS membershiprole")
    op.execute("DROP TYPE IF EXISTS eventstatus")
