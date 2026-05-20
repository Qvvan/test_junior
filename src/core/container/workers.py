from src.core.container.services import ServiceContainer
from src.core.logger import AppLogger
from src.workers.scheduler import AsyncScheduler


class WorkerContainer:
    __slots__ = ("_async_scheduler", "_logger", "_services")

    def __init__(self, logger: AppLogger, services: ServiceContainer):
        self._logger = logger
        self._services: ServiceContainer = services
        self._async_scheduler: AsyncScheduler | None = None


    @property
    def async_scheduler(self) -> AsyncScheduler:
        if not self._async_scheduler:
            self._async_scheduler = AsyncScheduler(
                logger=self._logger,
                workers=[]
            )
        return self._async_scheduler

    async def stop_workers(self) -> None:
        if self._async_scheduler:
            await self._async_scheduler.shutdown()
