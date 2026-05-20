import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.core.logger import AppLogger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP запросов."""

    def __init__(self, app: ASGIApp, logger: AppLogger) -> None:
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next) -> Response | None:
        request_id = str(uuid.uuid4())
        AppLogger.set_request_id(request_id)

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            self.logger.info(
                "HTTP request",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                client_ip=self._get_client_ip(request),
            )

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000

            self.logger.error(
                "HTTP request failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                client_ip=self._get_client_ip(request),
                error=f"{type(e).__name__}: {e}",
            )
            raise

        finally:
            AppLogger.clear_request_id()

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Получить IP клиента с учётом прокси."""
        if forwarded := request.headers.get("x-forwarded-for"):
            return forwarded.split(",")[0].strip()

        if real_ip := request.headers.get("x-real-ip"):
            return real_ip.strip()

        if request.client:
            return request.client.host

        return "unknown"
