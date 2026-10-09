from logging.config import fileConfig
from sqlmodel import SQLModel, create_engine
from alembic import context
from decouple import config as decouple_config
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import models

# This is the important line
target_metadata = SQLModel.metadata

# Get URL from environment (override alembic.ini)
db_url = decouple_config("DATABASE_URL", default="postgresql://user:pass@localhost/budgetdb")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # just directly use the db url so its sync and easy to override
    connectable = create_engine(db_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
