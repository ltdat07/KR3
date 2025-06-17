# orders-service/migrations/versions/0002_add_outbox_columns.py

"""add aggregate columns to outbox_events

Revision ID: 0002_add_outbox_columns
Revises: 0001_create_orders_and_outbox
Create Date: 2025-06-17 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision = '0002_add_outbox_columns'
down_revision = '0001_create_orders_and_outbox'
branch_labels = None
depends_on = None

def upgrade():
    # добавляем колонки
    op.add_column('outbox_events', sa.Column('aggregate_type', sa.String(), nullable=False, server_default='order'))
    op.add_column('outbox_events', sa.Column('aggregate_id', pg.UUID(as_uuid=True), nullable=False))
    op.add_column('outbox_events', sa.Column('event_type', sa.String(), nullable=False, server_default='order_created'))
    op.add_column('outbox_events', sa.Column('payload', sa.JSON(), nullable=False))
    op.add_column('outbox_events', sa.Column('processed', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('outbox_events', sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')))
    # создаём индекс на aggregate_id
    op.create_index('ix_outbox_events_aggregate_id', 'outbox_events', ['aggregate_id'])

def downgrade():
    op.drop_index('ix_outbox_events_aggregate_id', table_name='outbox_events')
    op.drop_column('outbox_events', 'created_at')
    op.drop_column('outbox_events', 'processed')
    op.drop_column('outbox_events', 'payload')
    op.drop_column('outbox_events', 'event_type')
    op.drop_column('outbox_events', 'aggregate_id')
    op.drop_column('outbox_events', 'aggregate_type')
