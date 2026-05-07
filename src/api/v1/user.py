from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import get_account_service, get_auth_service, require_role
from src.api.v1.schemas.auth import MessageResponse
from src.api.v1.schemas.context import AuthUser
from src.api.v1.schemas.user import (
    AdminPasswordUpdateRequest,
    UserResponse,
    UserUpdateRequest,
)
from src.domain.entities.account import AccountRole
from src.services.account_service import AccountService
from src.services.auth_service import AuthService

router = APIRouter(prefix="/user", tags=["user"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: AuthUser = Depends(require_role(AccountRole.ADMIN)),
    account_service: AccountService = Depends(get_account_service),
) -> list[UserResponse]:
    accounts = await account_service.list_accounts(limit=limit, offset=offset)
    return [UserResponse.model_validate(account) for account in accounts]


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    auth_user: AuthUser = Depends(require_role(AccountRole.USER, AccountRole.ADMIN)),
    account_service: AccountService = Depends(get_account_service),
) -> UserResponse:
    account = await account_service.get_me(auth_user.account_id)
    return UserResponse.model_validate(account)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    request: UserUpdateRequest,
    auth_user: AuthUser = Depends(require_role(AccountRole.USER, AccountRole.ADMIN)),
    account_service: AccountService = Depends(get_account_service),
) -> UserResponse:
    account = await account_service.update_profile(
        account_id=auth_user.account_id,
        first_name=request.first_name,
        last_name=request.last_name,
    )
    return UserResponse.model_validate(account)


@router.delete("/me", response_model=MessageResponse)
async def delete_my_account(
    auth_user: AuthUser = Depends(require_role(AccountRole.USER, AccountRole.ADMIN)),
    account_service: AccountService = Depends(get_account_service),
) -> MessageResponse:
    await account_service.set_status(auth_user.account_id, is_active=False)
    return MessageResponse(message="Account deactivated")


@router.post("/{account_id}/deactivate", response_model=MessageResponse)
async def admin_deactivate_user(
    account_id: UUID,
    _: AuthUser = Depends(require_role(AccountRole.ADMIN)),
    account_service: AccountService = Depends(get_account_service),
) -> MessageResponse:
    await account_service.set_status(
        account_id=account_id,
        is_active=False
    )
    return MessageResponse(message="Account deactivated")


@router.post("/{account_id}/activate", response_model=MessageResponse)
async def admin_activate_user(
    account_id: UUID,
    _: AuthUser = Depends(require_role(AccountRole.ADMIN)),
    account_service: AccountService = Depends(get_account_service),
) -> MessageResponse:
    await account_service.set_status(account_id, is_active=True)
    return MessageResponse(message="Account activated")


@router.patch("/{account_id}/password", response_model=MessageResponse)
async def admin_update_user_password(
    account_id: UUID,
    request: AdminPasswordUpdateRequest,
    _: AuthUser = Depends(require_role(AccountRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    await auth_service.admin_set_password(account_id=account_id, new_password=request.new_password)
    return MessageResponse(message="Password updated")

