from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import engine_from_config, pool
from database.database import Base

# Logging configuration
from logging.config import fileConfig

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

# Database URL and Metadata
settings = Settings()
db_url = str(settings.ASYNC_DATABASE_URI)
target_metadata = Base.metadata

# Migration Functions
def run_migrations_offline():
    # ...

def do_run_migrations(connection):
    # ...

async def run_migrations_online():
    # ...

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())