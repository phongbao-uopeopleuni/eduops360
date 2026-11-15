import asyncio

from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class Database:
    def __init__(self, url: SecretStr | None):
        self.engine = None
        self.session_factory: async_sessionmaker[AsyncSession] | None = None
        if url is not None:
            self.engine = create_async_engine(
                url.get_secret_value(),
                pool_pre_ping=True,
                pool_timeout=3,
                connect_args={"connect_timeout": 3},
                hide_parameters=True,
            )
            self.session_factory = async_sessionmaker(
                self.engine,
                expire_on_commit=False,
                autoflush=False,
            )

    async def ping(self) -> bool:
        if self.engine is None:
            return False
        try:
            async with asyncio.timeout(5), self.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            return True
        except (SQLAlchemyError, OSError, TimeoutError):
            return False

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()
