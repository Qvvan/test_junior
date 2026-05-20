from abc import ABC, abstractmethod
from typing import Any


class IQueryExecutor(ABC):
    @abstractmethod
    async def fetch(self, query: str, *args: Any) -> list[Any]: ...

    @abstractmethod
    async def fetchrow(self, query: str, *args: Any) -> Any: ...

    @abstractmethod
    async def fetchval(self, query: str, *args: Any) -> Any: ...

    @abstractmethod
    async def execute(self, query: str, *args: Any) -> str: ...


__all__ = ["IQueryExecutor"]
