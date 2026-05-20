import asyncio
from abc import ABC, abstractmethod


class IWorker(ABC):
    @abstractmethod
    async def start(self, stop: asyncio.Event) -> None:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...
