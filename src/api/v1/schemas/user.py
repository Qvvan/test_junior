from uuid import UUID

from pydantic import BaseModel, Field


class UserUpdateRequest(BaseModel):
    first_name: str = Field(default="", max_length=128)
    last_name: str = Field(default="", max_length=128)


class AdminLoginUpdateRequest(BaseModel):
    login: str = Field(min_length=3, max_length=64)


class AdminPasswordUpdateRequest(BaseModel):
    new_password: str = Field(min_length=8, max_length=256)


class UserResponse(BaseModel):
    id: UUID
    login: str
    first_name: str
    last_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True
