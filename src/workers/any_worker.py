import asyncio
from typing import Any

from src.core.logger import AppLogger
from src.interfaces.workers.worker import IWorker


class AnyWorker(IWorker):
    """Воркер ничего не знает о бизнес-правилах, только вызывает сервис."""

    __slots__ = ("_any_service", "_interval", "_logger")

    def __init__(
        self,
        any_service: Any,
        logger: AppLogger,
        interval: float,
    ) -> None:
        self._any_service = any_service
        self._logger = logger
        self._interval = interval

    async def start(self, stop: asyncio.Event) -> None:
        self._logger.info("AnyWorker worker started")

        try:
            while not stop.is_set():
                try:
                    ...
                    #TODO вот тут был бы вызвал просто сервис
                except Exception as e:
                    self._logger.error(f"Critical error in AnyWorker: {e}")
                try:
                    await asyncio.wait_for(stop.wait(), timeout=self._interval)
                except TimeoutError:
                    continue
        finally:
            self._logger.info("AnyWorker worker stopped")

    @property
    def name(self) -> str:
        return "any_worker"
