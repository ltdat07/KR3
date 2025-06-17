from alembic import op

revision = '0002_uq_inbox_order'
down_revision = '0001_accounts_inbox_outbox'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_inbox_order
        ON inbox_events ((payload->>'order_id'));
    """)

def downgrade():
    op.execute("DROP INDEX IF EXISTS uq_inbox_order;")
