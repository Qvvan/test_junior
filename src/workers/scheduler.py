import asyncio

from src.core.logger import AppLogger
from src.interfaces.workers.worker import IWorker


class AsyncScheduler:
    def __init__(
        self,
        logger: AppLogger,
        workers: list[IWorker],
    ) -> None:
        self._logger = logger
        self._workers = workers
        self._stop_events = {w.name: asyncio.Event() for w in workers}
        self._tasks: list[asyncio.Task[None]] = []

    def _register_tasks(self) -> None:
        self._tasks = [
            asyncio.create_task(w.start(self._stop_events[w.name]))
            for w in self._workers
        ]

    def _stop_workers(self) -> None:
        for name, event in self._stop_events.items():
            event.set()
            self._logger.info(f"Stop signal sent to {name}")

    async def start(self) -> None:
        self._logger.info("Scheduler starting workers...")
        self._register_tasks()
        self._logger.info(f"Scheduler started {len(self._tasks)} workers")

    async def wait_until_done(self) -> None:
        if not self._tasks:
            return
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def shutdown(self) -> None:
        self._logger.info("Shutting down scheduler...")
        self._stop_workers()

        try:
            await asyncio.wait_for(
                self.wait_until_done(),
                timeout=30.0,
            )
            self._logger.info("All workers stopped gracefully")
        except TimeoutError:
            self._logger.warning("Some workers didn't stop gracefully, cancelling...")
            for task in self._tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._logger.info("All workers cancelled")
