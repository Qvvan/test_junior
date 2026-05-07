from collections.abc import Awaitable, Callable

import jwt
from fastapi import Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from uuid import UUID

from src.api.v1.schemas.context import AuthUser
from src.core.exceptions import ForbiddenError, UnauthorizedError
from src.domain.entities.account import AccountRole
from src.services.account_service import AccountService
from src.services.auth_service import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_account_service(request: Request) -> AccountService:
    return request.app.state.container.services.account_service


async def get_auth_service(request: Request) -> AuthService:
    return request.app.state.container.services.auth_service


def require_role(*allowed_roles: AccountRole) -> Callable[[Request], Awaitable[AuthUser]]:
    allowed = frozenset(role.value for role in allowed_roles)

    async def _dependency(
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    ) -> AuthUser:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise UnauthorizedError("Missing bearer token")
        token = credentials.credentials.strip()
        if not token:
            raise UnauthorizedError("Missing bearer token")
        secret_key = request.app.state.container.config.app.SECRET_KEY
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            account_id = UUID(payload["sub"])
            role = payload["role"]
            token_type = payload["type"]
        except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
            raise UnauthorizedError("Invalid access token") from exc
        if token_type != "access":
            raise UnauthorizedError("Invalid token type")
        account = await request.app.state.container.repos.account_repository.get_by_id(account_id)
        if account is None or not account.is_active:
            raise UnauthorizedError("Account is deactivated")
        user = AuthUser(account_id=account_id, role=role)
        if user.role not in allowed:
            raise ForbiddenError("Insufficient role")
        return user

    return _dependency

