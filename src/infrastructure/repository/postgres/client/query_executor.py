from src.interfaces.clients.db import IConnectionPool, IQueryExecutor


class PostgresQueryExecutor(IQueryExecutor):
    __slots__ = ["_connection_pool"]

    def __init__(self, connection_pool: IConnectionPool):
        self._connection_pool = connection_pool

    async def fetch(
            self,
            query,
            *args
    ) -> list:
        async with self._connection_pool.get_connection() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(
            self,
            query: str,
            *args
    ):
        async with self._connection_pool.get_connection() as connection:
            return await connection.fetchrow(query, *args)

    async def fetchval(
            self,
            query: str,
            *args
    ):
        async with self._connection_pool.get_connection() as connection:
            return await connection.fetchval(query, *args)

    async def execute(
            self,
            query: str,
            *args
    ) -> str:
        async with self._connection_pool.get_connection() as connection:
            return await connection.execute(query, *args)
