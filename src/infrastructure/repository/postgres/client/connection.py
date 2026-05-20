import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg

from src.interfaces.clients.db.connection import IConnectionPool


class PostgresConnectionPool(IConnectionPool):
    __slots__ = ("_dsn", "_pool", "_pool_lock", "_pool_size")

    def __init__(
        self,
        user: str,
        password: str,
        host: str,
        port: int,
        database: str,
        pool_size: int = 20,
    ):
        self._dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self._pool_size = pool_size
        self._pool: asyncpg.Pool | None = None
        self._pool_lock = asyncio.Lock()

    async def connect(self) -> None:
        self._pool = await asyncpg.create_pool(
            self._dsn,
            min_size=self._pool_size // 2,
            max_size=self._pool_size,
            command_timeout=10,
            statement_cache_size=1024,
        )

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        if not self._pool:
            async with self._pool_lock:
                if not self._pool:
                    await self.connect()
        async with self._pool.acquire() as connection:
            yield connection

    async def close(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None
