from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any


class IConnectionPool(ABC):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def get_connection(self) -> AsyncGenerator[Any, None]: ...

    @abstractmethod
    async def close(self) -> None: ...


__all__ = ["IConnectionPool"]
