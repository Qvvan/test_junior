from src.core.container.infrastructure import InfrastructureContainer
from src.infrastructure.repository.postgres.account_repository import PostgresAccountRepository
from src.infrastructure.repository.postgres.auth_repository import PostgresAuthRepository
from src.interfaces.repositories import (
    IAccountRepository,
    IAuthRepository,
)


class RepositoryContainer:
    __slots__ = (
        "_account_repository",
        "_auth_repository",
        "_infra",
    )

    def __init__(self, infra: InfrastructureContainer):
        self._infra = infra
        self._account_repository: IAccountRepository | None = None
        self._auth_repository: IAuthRepository | None = None

    @property
    def account_repository(self) -> IAccountRepository:
        if not self._account_repository:
            self._account_repository = PostgresAccountRepository(query_executor=self._infra.query_executor)
        return self._account_repository

    @property
    def auth_repository(self) -> IAuthRepository:
        if not self._auth_repository:
            self._auth_repository = PostgresAuthRepository(query_executor=self._infra.query_executor)
        return self._auth_repository