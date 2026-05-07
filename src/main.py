from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.api import router
from src.api.exception_handlers import register_errors
from src.core.config import Config
from src.core.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""

    container = app.state.container

    yield

    await container.closer()


def create_app() -> FastAPI:
    """Фабрика для создания приложения"""

    cfg = Config()
    container = Container(cfg)

    app = FastAPI(
        title="API",
        description="API",
        version="1.0.0",
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        docs_url="/docs" if cfg.app.DEBUG else None,
        redoc_url="/redoc" if cfg.app.DEBUG else None,
        openapi_url="/openapi.json" if cfg.app.DEBUG else None,
    )

    app.add_middleware(
        CORSMiddleware,  #type: ignore
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.state.container = container

    app.include_router(router, prefix="/api")
    register_errors(app)

    return app
