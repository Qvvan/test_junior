from src.core.config import Config
from src.infrastructure.repository.postgres.client.connection import PostgresConnectionPool
from src.infrastructure.repository.postgres.client.query_executor import PostgresQueryExecutor
from src.interfaces.clients import IConnectionPool, IQueryExecutor


class InfrastructureContainer:
    def __init__(self, config: Config):
        self._config = config
        self._postgres: IConnectionPool | None = None
        self._query_executor: IQueryExecutor | None = None

    @property
    def postgres_db(self) -> IConnectionPool:
        if not self._postgres:
            self._postgres = PostgresConnectionPool(
                user=self._config.postgres.USER,
                password=self._config.postgres.PASSWORD.get_secret_value(),
                host=self._config.postgres.HOST,
                port=self._config.postgres.PORT,
                database=self._config.postgres.DATABASE,
                pool_size=self._config.postgres.POOL_SIZE,
            )
        return self._postgres

    @property
    def query_executor(self) -> IQueryExecutor:
        if not self._query_executor:
            self._query_executor = PostgresQueryExecutor(connection_pool=self.postgres_db)
        return self._query_executor

    @property
    def config(self) -> Config:
        return self._config

    async def closer(self) -> None:
        if self._postgres:
            await self._postgres.close()
