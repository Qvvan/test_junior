from src.core.container.infrastructure import InfrastructureContainer
from src.core.container.repositories import RepositoryContainer
from src.services import AccountService, AuthService


class ServiceContainer:

    def __init__(self, repos: RepositoryContainer, infra: InfrastructureContainer):
        self._infra = infra
        self._repos = repos
        self._account_service: AccountService | None = None
        self._auth_service: AuthService | None = None

    @property
    def account_service(self) -> AccountService:
        if not self._account_service:
            self._account_service = AccountService(
                account_repository=self._repos.account_repository,
                auth_repository=self._repos.auth_repository,
            )
        return self._account_service

    @property
    def auth_service(self) -> AuthService:
        if not self._auth_service:
            self._auth_service = AuthService(
                account_repository=self._repos.account_repository,
                auth_repository=self._repos.auth_repository,
                secret_key=self._infra.config.app.SECRET_KEY,
                access_ttl_minutes=self._infra.config.app.AUTH_ACCESS_TOKEN_TTL_MINUTES,
                refresh_ttl_days=self._infra.config.app.AUTH_REFRESH_TOKEN_TTL_DAYS,
            )
        return self._auth_service
