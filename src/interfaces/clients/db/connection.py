from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any


class IConnectionPool(ABC):
    @abstractmethod
    async def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_connection(self) -> AsyncGenerator[Any, None]:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError


__all__ = ["IConnectionPool"]
