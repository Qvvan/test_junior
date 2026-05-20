import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

import orjson

request_context: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
            "logger": record.name,
        }

        fields = getattr(record, "fields", None)
        if isinstance(fields, dict):
            payload.update(fields)

        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            payload["exception"] = {
                "type": exc_type.__name__ if exc_type else None,
                "message": str(exc_value) if exc_value else None,
                "traceback": self.formatException(record.exc_info),
            }

        return orjson.dumps(payload, default=str).decode()


class AppLogger:
    _logger: logging.Logger | None = None
    _configured: bool = False

    def __init__(self, level: str = "INFO", json_format: bool = True):
        self._level = level.upper()
        self._configure(json_format)

    def _configure(self, json_format: bool) -> None:
        if AppLogger._configured:
            return
        logger = logging.getLogger("app")
        logger.setLevel(self._level)
        logger.propagate = False
        handler = logging.StreamHandler(sys.stdout)
        formatter: logging.Formatter = (
            JsonFormatter() if json_format
            else logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        handler.setFormatter(formatter)
        logger.handlers.clear()
        logger.addHandler(handler)
        AppLogger._configured = True
        AppLogger._logger = logger

    @classmethod
    def set_request_id(cls, request_id: str) -> None:
        request_context.set(request_id)

    @classmethod
    def clear_request_id(cls) -> None:
        request_context.set(None)

    @classmethod
    def _get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            raise RuntimeError("AppLogger not initialized — call AppLogger() before use")
        return cls._logger

    @staticmethod
    def _extra(fields: dict[str, Any]) -> dict[str, Any]:
        return {"request_id": request_context.get(), "fields": fields}

    def debug(self, message: str, **fields: Any) -> None:
        self._get_logger().debug(message, extra=self._extra(fields))

    def info(self, message: str, **fields: Any) -> None:
        self._get_logger().info(message, extra=self._extra(fields))

    def warning(self, message: str, **fields: Any) -> None:
        self._get_logger().warning(message, extra=self._extra(fields))

    def error(self, message: str, **fields: Any) -> None:
        has_active_exception = sys.exc_info()[0] is not None
        self._get_logger().error(
            message,
            extra=self._extra(fields),
            exc_info=has_active_exception,
        )

    def critical(self, message: str, **fields: Any) -> None:
        self._get_logger().critical(message, extra=self._extra(fields))
