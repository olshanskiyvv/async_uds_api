from __future__ import annotations

from typing import Optional


class UDSAPIError(Exception):
    """
    Базовое исключение для ошибок UDS Partner API.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        error_code: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class UDSBadRequestError(UDSAPIError):
    """
    Ошибка валидации или бизнес-логики (HTTP 400).
    """


class UDSUnauthorizedError(UDSAPIError):
    """
    Неверные company_id или api_key (HTTP 401).
    """


class UDSForbiddenError(UDSAPIError):
    """
    Доступ запрещён или недостаточно прав (HTTP 403).
    """


class UDSNotFoundError(UDSAPIError):
    """
    Объект или метод не найдены (HTTP 404).
    """


class UDSUnexpectedError(UDSAPIError):
    """
    Любая другая ошибка от API.
    """


class UDSImageError(Exception):
    """
    Базовое исключение для ошибок загрузки изображений.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class UDSImageReadError(UDSImageError):
    """
    Ошибка чтения файла изображения.
    """
    pass


class UDSImageDownloadError(UDSImageError):
    """
    Ошибка скачивания изображения по URL.
    """
    pass


class UDSImageUploadError(UDSImageError):
    """
    Ошибка загрузки изображения на сервер.
    """
    pass


class UDSImageUnsupportedSourceError(UDSImageError):
    """
    Неподдерживаемый источник изображения.
    """
    pass

