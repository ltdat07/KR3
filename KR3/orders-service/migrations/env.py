from logging.config import fileConfig
import os, sys

# Чтобы Alembic видел ваш код:
this_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(this_dir, os.pardir))
sys.path.insert(0, project_root)

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

# Подключаем метаданные наших моделей
from models.schema import Base
...


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Устанавливаем путь к скриптам миграций
# (это уже прописано в alembic.ini: script_location = migrations)

# Настраиваем логирование из alembic.ini
fileConfig(config.config_file_name)

# Целевая metadata для autogenerate (если понадобится)
target_metadata = Base.metadata

# Получаем URL из alembic.ini ([alembic] sqlalchemy.url)
# и приводим его к синхронному драйверу (удаляем +asyncpg, если он там есть)
sync_url = config.get_main_option("sqlalchemy.url").replace("+asyncpg", "")


def run_migrations_online():
    """Run migrations in 'online' mode with a synchronous engine."""
    connectable = create_engine(
        sync_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:  # type: Connection
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
