from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

revision = '0001_accounts_inbox_outbox'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():

    op.execute("DROP TABLE IF EXISTS outbox_events")
    op.execute("DROP TABLE IF EXISTS inbox_events")
    op.execute("DROP TABLE IF EXISTS accounts")

    # accounts
    op.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            user_id UUID PRIMARY KEY,
            balance NUMERIC(12,2) NOT NULL DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)

    # inbox_events
    op.execute("""
        CREATE TABLE IF NOT EXISTS inbox_events (
            id UUID PRIMARY KEY,
            event_type VARCHAR NOT NULL,
            payload JSON NOT NULL,
            processed BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
    """)

    # outbox_events
    op.execute("""
        CREATE TABLE IF NOT EXISTS outbox_events (
            id UUID PRIMARY KEY,
            event_type VARCHAR NOT NULL,
            payload JSON NOT NULL,
            processed BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
        )
    """)

def downgrade():
    op.execute("DROP TABLE IF EXISTS outbox_events")
    op.execute("DROP TABLE IF EXISTS inbox_events")
    op.execute("DROP TABLE IF EXISTS accounts")
