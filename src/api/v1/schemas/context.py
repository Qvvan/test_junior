from uuid import UUID

from pydantic import BaseModel


class AuthUser(BaseModel):
    account_id: UUID
    role: str
