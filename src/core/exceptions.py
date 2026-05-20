from starlette import status


class AppError(Exception):
    """Базовое исключение приложения"""
    http_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    __slots__ = ("code", "message")

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ValidationError(AppError):
    """Исключения валидации"""
    http_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class NotFoundError(AppError):
    """Сущность не найдена"""
    http_status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, entity: str, identifier: str):
        message = f"{entity} with identifier '{identifier}' not found"
        super().__init__(message, "NOT_FOUND")


class ConflictError(AppError):
    """Конфликт данных"""
    http_status_code = status.HTTP_409_CONFLICT


    def __init__(self, message: str):
        super().__init__(message, "CONFLICT")


class ForbiddenError(AppError):
    """Ошибка доступа (403 Forbidden)"""
    http_status_code = status.HTTP_403_FORBIDDEN

    def __init__(self, message: str = "Доступ запрещен"):
        super().__init__(message, "FORBIDDEN")


class UnauthorizedError(AppError):
    """Ошибка аутентификации (401 Unauthorized)"""
    http_status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self, message: str = "Требуется аутентификация"):
        super().__init__(message, "UNAUTHORIZED")
