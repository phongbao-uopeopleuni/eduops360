from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Provide one database session per request and always close it."""
    factory = request.app.state.database.session_factory
    if factory is None:
        raise AppError(503, "DATABASE_UNAVAILABLE", "Cơ sở dữ liệu chưa sẵn sàng.")
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
