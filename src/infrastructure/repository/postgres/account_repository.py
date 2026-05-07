from uuid import UUID

from src.domain.entities.account import Account
from src.interfaces.clients.db import IQueryExecutor
from src.interfaces.repositories import IAccountRepository


class PostgresAccountRepository(IAccountRepository):
    __slots__ = ("_query_executor",)

    def __init__(self, query_executor: IQueryExecutor) -> None:
        self._query_executor = query_executor

    async def exists_by_login(self, login: str) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM accounts WHERE login = $1)"
        return bool(await self._query_executor.fetchval(query, login))

    async def create(self, account: Account) -> Account:
        query = """
            INSERT INTO accounts (login, password_hash, first_name, last_name, role, is_active)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id, login, password_hash, first_name, last_name, role, is_active, created_at, updated_at
        """
        row = await self._query_executor.fetchrow(
            query,
            account.login,
            account.password_hash,
            account.first_name,
            account.last_name,
            account.role,
            account.is_active,
        )
        return self._row_to_account(row)

    async def get_by_id(self, account_id: UUID) -> Account | None:
        query = """
            SELECT id, login, password_hash, first_name, last_name, role, is_active, created_at, updated_at
            FROM accounts
            WHERE id = $1
        """
        row = await self._query_executor.fetchrow(query, account_id)
        return self._row_to_account(row) if row else None

    async def get_by_login(self, login: str) -> Account | None:
        query = """
            SELECT id, login, password_hash, first_name, last_name, role, is_active, created_at, updated_at
            FROM accounts
            WHERE login = $1
        """
        row = await self._query_executor.fetchrow(query, login)
        return self._row_to_account(row) if row else None

    async def list_accounts(self, limit: int = 50, offset: int = 0) -> list[Account]:
        query = """
            SELECT id, login, password_hash, first_name, last_name, role, is_active, created_at, updated_at
            FROM accounts
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """
        rows = await self._query_executor.fetch(query, limit, offset)
        return [self._row_to_account(row) for row in rows]

    async def update_login(self, account_id: UUID, login: str) -> Account | None:
        query = """
            UPDATE accounts
            SET login = $2, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
            RETURNING id, login, password_hash, first_name, last_name, role, is_active, created_at, updated_at
        """
        row = await self._query_executor.fetchrow(query, account_id, login)
        return self._row_to_account(row) if row else None

    async def update_password_hash(self, account_id: UUID, password_hash: str) -> bool:
        query = """
            UPDATE accounts
            SET password_hash = $2, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """
        result = await self._query_executor.execute(query, account_id, password_hash)
        return result.endswith("1")

    async def update_profile(self, account_id: UUID, first_name: str, last_name: str) -> Account | None:
        query = """
            UPDATE accounts
            SET first_name = $2, last_name = $3, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
            RETURNING id, login, password_hash, first_name, last_name, role, is_active, created_at, updated_at
        """
        row = await self._query_executor.fetchrow(query, account_id, first_name, last_name)
        return self._row_to_account(row) if row else None

    async def deactivate(self, account_id: UUID) -> bool:
        query = """
            UPDATE accounts
            SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """
        result = await self._query_executor.execute(query, account_id)
        return result.endswith("1")

    async def activate(self, account_id: UUID) -> bool:
        query = """
            UPDATE accounts
            SET is_active = TRUE, updated_at = CURRENT_TIMESTAMP
            WHERE id = $1
        """
        result = await self._query_executor.execute(query, account_id)
        return result.endswith("1")

    @staticmethod
    def _row_to_account(row) -> Account:
        return Account(
            id=row["id"],
            login=row["login"],
            password_hash=row["password_hash"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            role=row["role"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
