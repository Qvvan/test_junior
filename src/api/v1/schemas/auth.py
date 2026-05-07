from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    login: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=256)
    first_name: str = Field(default="", max_length=128)
    last_name: str = Field(default="", max_length=128)


class LoginRequest(BaseModel):
    login: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=256)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=8, max_length=256)
    new_password: str = Field(min_length=8, max_length=256)
    new_password_confirm: str = Field(min_length=8, max_length=256)


class AccountPublicResponse(BaseModel):
    id: str
    login: str
    first_name: str
    last_name: str


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    account: AccountPublicResponse
    tokens: TokenPairResponse


class MessageResponse(BaseModel):
    message: str

