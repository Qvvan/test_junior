from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

class AccountRole(StrEnum):
    USER = "user"
    ADMIN = "admin"
    SERVICE = "service"


@dataclass(frozen=True, slots=True)
class Account:
    login: str
    password_hash: str
    first_name: str = ""
    last_name: str = ""
    role: str = AccountRole.USER
    is_active: bool = True
    id: UUID | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

