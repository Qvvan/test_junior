from datetime import datetime
from uuid import UUID

from src.domain.entities.auth import RefreshTokenRecord
from src.interfaces.clients.db import IQueryExecutor
from src.interfaces.repositories import IAuthRepository


class PostgresAuthRepository(IAuthRepository):
    __slots__ = ("_query_executor",)

    def __init__(self, query_executor: IQueryExecutor) -> None:
        self._query_executor = query_executor

    async def create_refresh_token(
        self,
        jti: UUID,
        account_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshTokenRecord:
        query = """
            INSERT INTO account_refresh_tokens (jti, account_id, token_hash, expires_at)
            VALUES ($1, $2, $3, $4)
            RETURNING jti, account_id, token_hash, expires_at, revoked_at, created_at
        """
        row = await self._query_executor.fetchrow(query, jti, account_id, token_hash, expires_at)
        return self._row_to_refresh(row)

    async def get_refresh_token_by_jti(self, jti: UUID) -> RefreshTokenRecord | None:
        query = """
            SELECT jti, account_id, token_hash, expires_at, revoked_at, created_at
            FROM account_refresh_tokens
            WHERE jti = $1
        """
        row = await self._query_executor.fetchrow(query, jti)
        if not row:
            return None
        return self._row_to_refresh(row)

    async def revoke_refresh_token(self, jti: UUID) -> bool:
        query = """
            UPDATE account_refresh_tokens
            SET revoked_at = CURRENT_TIMESTAMP
            WHERE jti = $1
              AND revoked_at IS NULL
        """
        result = await self._query_executor.execute(query, jti)
        return result.endswith("1")

    async def revoke_all_refresh_tokens_for_account(self, account_id: UUID) -> int:
        query = """
            UPDATE account_refresh_tokens
            SET revoked_at = CURRENT_TIMESTAMP
            WHERE account_id = $1
              AND revoked_at IS NULL
        """
        result = await self._query_executor.execute(query, account_id)
        try:
            return int(str(result).split()[-1])
        except (ValueError, IndexError):
            return 0

    @staticmethod
    def _row_to_refresh(row) -> RefreshTokenRecord:
        return RefreshTokenRecord(
            jti=row["jti"],
            account_id=row["account_id"],
            token_hash=row["token_hash"],
            expires_at=row["expires_at"],
            revoked_at=row["revoked_at"],
            created_at=row["created_at"],
        )
