from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_auth_service, require_role
from src.api.v1.schemas.context import AuthUser
from src.api.v1.schemas.auth import (
    AccountPublicResponse,
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenPairResponse,
)
from src.domain.entities.account import AccountRole
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    account, tokens = await auth_service.register(
        login=request.login,
        password=request.password,
        first_name=request.first_name,
        last_name=request.last_name,
    )
    return _build_auth_response(account, tokens)


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    account, tokens = await auth_service.login(
        login=request.login,
        password=request.password,
    )
    return _build_auth_response(account, tokens)


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(
    request: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPairResponse:
    tokens = await auth_service.refresh(request.refresh_token)
    return TokenPairResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    auth_user: AuthUser = Depends(require_role(AccountRole.USER, AccountRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    await auth_service.change_password(
        account_id=auth_user.account_id,
        old_password=request.old_password,
        new_password=request.new_password,
        new_password_confirm=request.new_password_confirm,
    )
    return MessageResponse(message="Password updated")


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    await auth_service.logout(request.refresh_token)
    return MessageResponse(message="Logged out")


def _build_auth_response(account, tokens) -> AuthResponse:
    return AuthResponse(
        account=AccountPublicResponse(
            id=str(account.id),
            login=account.login,
            first_name=account.first_name,
            last_name=account.last_name,
        ),
        tokens=TokenPairResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type=tokens.token_type,
        ),
    )
