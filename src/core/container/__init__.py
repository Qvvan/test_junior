from src.core.config import Config
from src.core.container.infrastructure import InfrastructureContainer
from src.core.container.repositories import RepositoryContainer
from src.core.container.services import ServiceContainer
from src.core.container.workers import WorkerContainer
from src.core.logger import AppLogger


class Container:
    __slots__ = (
        "config",
        "infra",
        "logger",
        "repos",
        "services",
        "workers",
    )

    def __init__(self, config: Config):
        self.config = config
        self.logger = AppLogger(level=config.logging.LEVEL, json_format=config.logging.JSON_FORMAT)
        self.infra = InfrastructureContainer(config=config)
        self.repos = RepositoryContainer(infra=self.infra)
        self.services = ServiceContainer(logger=self.logger, repos=self.repos, infra=self.infra)
        self.workers = WorkerContainer(logger=self.logger, services=self.services)

    async def closer(self) -> None:
        await self.workers.stop_workers()
        await self.infra.closer()


__all__ = [
    "Container",
    "InfrastructureContainer",
    "RepositoryContainer",
    "ServiceContainer",
    "WorkerContainer",
]
