from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.requests import Request

from src.core.exceptions import AppError


def register_errors(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(req: Request, exc: AppError) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=exc.http_status_code,
            content={"status": "error", "code": exc.code, "comment": exc.message, "obj": None},
        )
