from abc import ABC, abstractmethod
from typing import Any


class IQueryExecutor(ABC):
    @abstractmethod
    async def fetch(self, query: str, *args: Any) -> list[Any]:
        raise NotImplementedError

    @abstractmethod
    async def fetchrow(self, query: str, *args: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def fetchval(self, query: str, *args: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def execute(self, query: str, *args: Any) -> Any:
        raise NotImplementedError


__all__ = ["IQueryExecutor"]
