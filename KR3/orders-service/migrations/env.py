from logging.config import fileConfig
import os, sys

this_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(this_dir, os.pardir))
sys.path.insert(0, project_root)

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from models.schema import Base

config = context.config

fileConfig(config.config_file_name)

target_metadata = Base.metadata

sync_url = config.get_main_option("sqlalchemy.url").replace("+asyncpg", "")


def run_migrations_online():
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # отслеживать изменения типов колонок
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise NotImplementedError("Offline mode is not supported")
else:
    run_migrations_online()
