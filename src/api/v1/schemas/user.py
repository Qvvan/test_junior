from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.entities.account import AccountRole


class UserUpdateRequest(BaseModel):
    first_name: str = Field(default="", max_length=128)
    last_name: str = Field(default="", max_length=128)


class AdminPasswordUpdateRequest(BaseModel):
    new_password: str = Field(min_length=8, max_length=256)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    login: str
    first_name: str
    last_name: str
    role: AccountRole
    is_active: bool
