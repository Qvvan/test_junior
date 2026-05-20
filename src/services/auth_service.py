import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from src.core.exceptions import ConflictError, NotFoundError, UnauthorizedError, ValidationError
from src.core.logger import AppLogger
from src.domain.entities.account import Account
from src.domain.entities.auth import TokenPair
from src.interfaces.repositories import IAccountRepository, IAuthRepository

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
MIN_PASSWORD_LENGTH = 8

_PASSWORD_HASHER = PasswordHasher()
_DUMMY_HASH = _PASSWORD_HASHER.hash("dummy")


def decode_token(token: str, secret_key: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError("Invalid token") from exc
    if payload.get("type") != expected_type:
        raise UnauthorizedError("Invalid token type")
    return payload


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        return _PASSWORD_HASHER.verify(stored_hash, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(
        self,
        account_repository: IAccountRepository,
        auth_repository: IAuthRepository,
        logger: AppLogger,
        secret_key: str,
        access_ttl_minutes: int = 15,
        refresh_ttl_days: int = 30,
    ) -> None:
        self._account_repository = account_repository
        self._auth_repository = auth_repository
        self._secret_key = secret_key
        self._logger = logger
        self._access_ttl = timedelta(minutes=access_ttl_minutes)
        self._refresh_ttl = timedelta(days=refresh_ttl_days)

    async def register(
        self,
        login: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
    ) -> tuple[Account, TokenPair]:
        normalized_login = self._normalize_login(login)
        if not normalized_login:
            raise ValidationError("Login is required")
        self._validate_password(password)

        if await self._account_repository.exists_by_login(normalized_login):
            raise ConflictError("Account with this login already exists")

        password_hash = _PASSWORD_HASHER.hash(password)
        created_account = await self._account_repository.create(
            Account(
                login=normalized_login,
                password_hash=password_hash,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
            )
        )
        tokens = await self._issue_token_pair(created_account.id, created_account.role)
        return created_account, tokens

    async def login(self, login: str, password: str) -> tuple[Account, TokenPair]:
        normalized_login = self._normalize_login(login)
        account = await self._account_repository.get_by_login(normalized_login)
        if account is None:
            _verify_password(password, _DUMMY_HASH)  # constant-time guard against timing attacks
            raise UnauthorizedError("Invalid login or password")
        if not _verify_password(password, account.password_hash):
            raise UnauthorizedError("Invalid login or password")
        if not account.is_active:
            raise UnauthorizedError("Account is deactivated")
        tokens = await self._issue_token_pair(account.id, account.role)
        return account, tokens

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = self._decode_token(refresh_token, expected_type=REFRESH_TOKEN_TYPE)
        try:
            jti = UUID(payload["jti"])
            account_id = UUID(payload["sub"])
        except (KeyError, ValueError) as exc:
            raise UnauthorizedError("Invalid token payload") from exc

        refresh_record = await self._auth_repository.get_refresh_token_by_jti(jti)
        if not refresh_record:
            raise UnauthorizedError("Refresh token not found")
        if refresh_record.revoked_at is not None:
            raise UnauthorizedError("Refresh token revoked")
        if self._to_naive_utc(refresh_record.expires_at) < self._utc_now_naive():
            raise UnauthorizedError("Refresh token expired")

        incoming_hash = _hash_token(refresh_token)
        if not hmac.compare_digest(refresh_record.token_hash, incoming_hash):
            raise UnauthorizedError("Refresh token mismatch")

        account = await self._account_repository.get_by_id(account_id)
        if not account:
            raise UnauthorizedError("Account not found")
        if not account.is_active:
            raise UnauthorizedError("Account is deactivated")

        await self._auth_repository.revoke_refresh_token(jti)
        return await self._issue_token_pair(account_id, account.role)

    async def logout(self, refresh_token: str) -> None:
        payload = self._decode_token(refresh_token, expected_type=REFRESH_TOKEN_TYPE)
        try:
            jti = UUID(payload["jti"])
        except (KeyError, ValueError) as exc:
            raise UnauthorizedError("Invalid token payload") from exc
        await self._auth_repository.revoke_refresh_token(jti)

    async def change_password(
        self,
        account_id: UUID,
        old_password: str,
        new_password: str,
        new_password_confirm: str,
    ) -> None:
        if new_password != new_password_confirm:
            raise ValidationError("Passwords do not match")
        self._validate_password(new_password)
        if old_password == new_password:
            raise ValidationError("New password must be different from old password")

        account = await self._account_repository.get_by_id(account_id)
        if not account:
            raise NotFoundError("Account", str(account_id))
        if not _verify_password(old_password, account.password_hash):
            raise UnauthorizedError("Current password is invalid")

        password_hash = _PASSWORD_HASHER.hash(new_password)
        updated = await self._account_repository.update_password_hash(account_id, password_hash)
        if not updated:
            raise UnauthorizedError("Account not found")
        await self._auth_repository.revoke_all_refresh_tokens_for_account(account_id)

    async def admin_set_password(self, account_id: UUID, new_password: str) -> None:
        self._validate_password(new_password)
        password_hash = _PASSWORD_HASHER.hash(new_password)
        updated = await self._account_repository.update_password_hash(account_id, password_hash)
        if not updated:
            raise NotFoundError("Account", str(account_id))
        await self._auth_repository.revoke_all_refresh_tokens_for_account(account_id)

    async def _issue_token_pair(self, account_id: UUID, role: str) -> TokenPair:
        now = self._utc_now_naive()
        access_expires = now + self._access_ttl
        refresh_expires = now + self._refresh_ttl
        refresh_jti = uuid4()

        access_payload = {
            "sub": str(account_id),
            "role": role,
            "type": ACCESS_TOKEN_TYPE,
            "iat": int(now.timestamp()),
            "exp": int(access_expires.timestamp()),
        }
        refresh_payload = {
            "sub": str(account_id),
            "role": role,
            "jti": str(refresh_jti),
            "type": REFRESH_TOKEN_TYPE,
            "iat": int(now.timestamp()),
            "exp": int(refresh_expires.timestamp()),
        }

        access_token = jwt.encode(access_payload, self._secret_key, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, self._secret_key, algorithm="HS256")

        await self._auth_repository.create_refresh_token(
            jti=refresh_jti,
            account_id=account_id,
            token_hash=_hash_token(refresh_token),
            expires_at=refresh_expires,
        )
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    def _decode_token(self, token: str, expected_type: str) -> dict:
        return decode_token(token, self._secret_key, expected_type)

    @staticmethod
    def _normalize_login(login: str) -> str:
        return login.strip().lower()

    @staticmethod
    def _validate_password(password: str) -> None:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValidationError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")

    @staticmethod
    def _utc_now_naive() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    @staticmethod
    def _to_naive_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone(UTC).replace(tzinfo=None)
