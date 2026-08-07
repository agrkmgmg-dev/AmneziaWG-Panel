from logging.config import fileConfig
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# -------------------------------------------------------
# Add project root to PYTHONPATH
# -------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# -------------------------------------------------------
# Alembic Config
# -------------------------------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------------
# Import SQLAlchemy metadata
# -------------------------------------------------------

from backend.app.db.base import Base

# Import ALL models so SQLAlchemy registers them
from backend.app.models.user import User
from backend.app.models.peer import Peer
from backend.app.models.traffic import Traffic
from backend.app.models.activity_log import ActivityLog

target_metadata = Base.metadata

# -------------------------------------------------------
# Offline migrations
# -------------------------------------------------------

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

# -------------------------------------------------------
# Online migrations
# -------------------------------------------------------

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# -------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()