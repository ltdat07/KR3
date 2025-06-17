from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

revision = '0001_create_orders_and_outbox'
down_revision = None
branch_labels = None
depends_on = None

# ENUM‑тип для статуса заказа
orderstatus_enum = pg.ENUM(
    'NEW', 'FINISHED', 'CANCELLED',
    name='orderstatus',
    create_type=False
)

def upgrade():
    op.execute("DROP TABLE IF EXISTS outbox_events CASCADE")
    op.execute("DROP TABLE IF EXISTS orders CASCADE")
    op.execute("DROP TYPE IF EXISTS orderstatus CASCADE")

    # создаём ENUM‑тип, если его нет
    op.execute("""
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_type WHERE typname = 'orderstatus'
      ) THEN
        CREATE TYPE orderstatus AS ENUM ('NEW','FINISHED','CANCELLED');
      END IF;
    END$$;
    """)

    # таблица orders
    op.create_table(
        'orders',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', pg.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('status', orderstatus_enum, nullable=False,
                  server_default=sa.text("'NEW'")),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True),
                  onupdate=sa.text('now()')),
    )
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])

    # таблица outbox_events
    op.create_table(
        'outbox_events',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('aggregate_type', sa.String, nullable=False),
        sa.Column('aggregate_id', pg.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String, nullable=False),
        sa.Column('payload', sa.JSON, nullable=False),
        sa.Column('processed', sa.Boolean, nullable=False,
                  server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True),
                  server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_outbox_events_aggregate_id', 'outbox_events', ['aggregate_id'])


def downgrade():
    op.drop_index('ix_outbox_events_aggregate_id', table_name='outbox_events')
    op.drop_table('outbox_events')
    op.drop_index('ix_orders_user_id', table_name='orders')
    op.drop_table('orders')
    op.execute("DROP TYPE IF EXISTS orderstatus")
