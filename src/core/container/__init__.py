from src.core.config import Config
from src.core.container.infrastructure import InfrastructureContainer
from src.core.container.repositories import RepositoryContainer
from src.core.container.services import ServiceContainer

class Container:
    __slots__ = (
        "config",
        "infra",
        "repos",
        "services",
    )

    def __init__(self, config: Config):
        self.config = config
        self.infra = InfrastructureContainer(config=config)
        self.repos = RepositoryContainer(infra=self.infra)
        self.services = ServiceContainer(repos=self.repos, infra=self.infra)

    async def closer(self) -> None:
        await self.infra.closer()


__all__ = [
    "Container",
    "InfrastructureContainer",
    "RepositoryContainer",
    "ServiceContainer",
]
