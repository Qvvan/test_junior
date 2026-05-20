from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.account import Account


class IAccountRepository(ABC):
    @abstractmethod
    async def exists_by_login(self, login: str) -> bool: ...

    @abstractmethod
    async def create(self, account: Account) -> Account: ...

    @abstractmethod
    async def get_by_id(self, account_id: UUID) -> Account | None: ...

    @abstractmethod
    async def get_by_login(self, login: str) -> Account | None: ...

    @abstractmethod
    async def list_accounts(self, limit: int = 50, offset: int = 0) -> list[Account]: ...

    @abstractmethod
    async def update_login(self, account_id: UUID, login: str) -> Account | None: ...

    @abstractmethod
    async def update_password_hash(self, account_id: UUID, password_hash: str) -> bool: ...

    @abstractmethod
    async def update_profile(self, account_id: UUID, first_name: str, last_name: str) -> Account | None: ...

    @abstractmethod
    async def deactivate(self, account_id: UUID) -> bool: ...

    @abstractmethod
    async def activate(self, account_id: UUID) -> bool: ...
