"""add unique index on inbox_events.payload->>'order_id'

Revision ID: 0002_uq_inbox_order
Revises: 0001_accounts_inbox_outbox
Create Date: 2025-06-XX XX:XX:XX

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '0002_uq_inbox_order'
down_revision = '0001_accounts_inbox_outbox'
branch_labels = None
depends_on = None

def upgrade():
    # создаём уникальный индекс на выражение payload->>'order_id'
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_inbox_order
        ON inbox_events ((payload->>'order_id'));
    """)

def downgrade():
    op.execute("DROP INDEX IF EXISTS uq_inbox_order;")
