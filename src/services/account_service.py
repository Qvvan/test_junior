from uuid import UUID

from src.core.exceptions import NotFoundError
from src.domain.entities.account import Account
from src.interfaces.repositories import IAccountRepository, IAuthRepository


class AccountService:
    def __init__(self, account_repository: IAccountRepository, auth_repository: IAuthRepository) -> None:
        self._account_repository = account_repository
        self._auth_repository = auth_repository

    async def get_me(self, account_id: UUID) -> Account:
        account = await self._account_repository.get_by_id(account_id)
        if not account:
            raise NotFoundError("Account", str(account_id))
        return account

    async def list_accounts(self, limit: int = 50, offset: int = 0) -> list[Account]:
        safe_limit = max(1, min(limit, 200))
        safe_offset = max(0, offset)
        return await self._account_repository.list_accounts(limit=safe_limit, offset=safe_offset)

    async def update_profile(self, account_id: UUID, first_name: str, last_name: str) -> Account:
        updated = await self._account_repository.update_profile(
            account_id=account_id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
        )
        if not updated:
            raise NotFoundError("Account", str(account_id))
        return updated

    async def set_status(self, account_id: UUID, is_active: bool) -> None:
        changed = (
            await self._account_repository.activate(account_id)
            if is_active
            else await self._account_repository.deactivate(account_id)
        )
        if not changed:
            raise NotFoundError("Account", str(account_id))
        if not is_active:
            await self._auth_repository.revoke_all_refresh_tokens_for_account(account_id)

