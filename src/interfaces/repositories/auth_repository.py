from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.entities.auth import RefreshTokenRecord


class IAuthRepository(ABC):
    @abstractmethod
    async def create_refresh_token(
        self,
        jti: UUID,
        account_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshTokenRecord:
        raise NotImplementedError

    @abstractmethod
    async def get_refresh_token_by_jti(self, jti: UUID) -> RefreshTokenRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def revoke_refresh_token(self, jti: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def revoke_all_refresh_tokens_for_account(self, account_id: UUID) -> int:
        raise NotImplementedError
