from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg

from src.interfaces.clients.db.connection import IConnectionPool


class PostgresConnectionPool(IConnectionPool):
    __slots__ = ["_pool", "dsn", "echo", "pool_size"]

    def __init__(
            self,
            user: str,
            password: str,
            host: str,
            port: int,
            database: str,
            echo: bool = False,
            pool_size: int = 20
    ):
        self.dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.echo = echo
        self.pool_size = pool_size
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Создает пул соединений с БД"""
        async def init_connection(connection):
            await connection.set_type_codec(
                'uuid',
                encoder=str,
                decoder=str,
                schema='pg_catalog'
            )

        self._pool = await asyncpg.create_pool(
            self.dsn,
            min_size=self.pool_size // 2,
            max_size=self.pool_size,
            command_timeout=10,
            statement_cache_size=1024,
            init=init_connection
        )

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        if not self._pool:
            await self.connect()

        async with self._pool.acquire() as connection:
            yield connection

    async def close(self) -> None:
        """Закрытие пула соединений"""
        if self._pool:
            await self._pool.close()
            self._pool = None
