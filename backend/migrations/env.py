import asyncio
import os

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import Settings
from app.core.event_loop import create_event_loop
from app.db.base import Base
from app.modules.academic_years import models as academic_year_models  # noqa: F401
from app.modules.audit_logs import models as audit_models  # noqa: F401

# Import models so Alembic sees them
from app.modules.auth import models as auth_models  # noqa: F401
from app.modules.school_calendar import models as school_calendar_models  # noqa: F401
from app.modules.students import models as student_models  # noqa: F401
from app.modules.timetables import models as timetable_models  # noqa: F401

config = context.config
if not os.environ.get("EDUOPS_DATABASE_URL"):
    raise RuntimeError("Set an explicit EDUOPS_DATABASE_URL before running migrations")
settings = Settings(_env_file=None)
if settings.database_url is None:  # defensive: the explicit value must also validate
    raise RuntimeError("Set an explicit EDUOPS_DATABASE_URL before running migrations")
database_url = settings.database_url.get_secret_value()
target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def apply_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    engine = create_async_engine(database_url, poolclass=pool.NullPool)
    try:
        async with engine.connect() as connection:
            await connection.run_sync(apply_migrations)
    finally:
        await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online(), loop_factory=create_event_loop)
