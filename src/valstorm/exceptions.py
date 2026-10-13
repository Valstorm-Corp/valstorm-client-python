"""Unified exception hierarchy for Valstorm Client SDK."""

from typing import Any


class ValstormError(Exception):
    """Base exception for all Valstorm SDK errors."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class TransportError(ValstormError):
    """Raised when a network connection, TLS, or DNS error occurs."""


class RequestTimeoutError(TransportError):
    """Raised when an HTTP request times out."""


class ValstormHttpError(ValstormError):
    """Raised when the Valstorm API returns a non-2xx status code."""

    def __init__(
        self,
        message: str,
        status_code: int,
        details: Any | None = None,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.details = details
        self.headers = headers or {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(status_code={self.status_code}, message={self.message!r})"
        )


class AuthenticationError(ValstormHttpError):
    """Raised on 401 Unauthorized (invalid, expired, or missing credentials)."""


class PermissionDeniedError(ValstormHttpError):
    """Raised on 403 Forbidden (insufficient Object/Field/Row-Level permissions)."""


class NotFoundError(ValstormHttpError):
    """Raised on 404 Not Found (resource, record, or vault does not exist)."""


class ConflictError(ValstormHttpError):
    """Raised on 409 Conflict (duplicate record, unique constraint collision)."""


class ValidationError(ValstormHttpError):
    """Raised on 422 Unprocessable Entity (schema validation failure)."""


class RateLimitError(ValstormHttpError):
    """Raised on 429 Too Many Requests."""

    def __init__(
        self,
        message: str,
        status_code: int = 429,
        details: Any | None = None,
        headers: dict[str, str] | None = None,
        retry_after: float | None = None,
    ):
        super().__init__(message, status_code, details, headers)
        self.retry_after = retry_after


class ServerError(ValstormHttpError):
    """Raised on 500+ Internal Server Error."""


def map_http_status_to_exception(
    status_code: int,
    message: str,
    details: Any | None = None,
    headers: dict[str, str] | None = None,
) -> ValstormHttpError:
    """Maps an HTTP status code to the appropriate specialized exception."""
    if status_code == 401:
        return AuthenticationError(message, status_code, details, headers)
    if status_code == 403:
        return PermissionDeniedError(message, status_code, details, headers)
    if status_code == 404:
        return NotFoundError(message, status_code, details, headers)
    if status_code == 409:
        return ConflictError(message, status_code, details, headers)
    if status_code == 422:
        return ValidationError(message, status_code, details, headers)
    if status_code == 429:
        retry_after = None
        if headers and "Retry-After" in headers:
            try:
                retry_after = float(headers["Retry-After"])
            except (ValueError, TypeError):
                pass
        return RateLimitError(message, status_code, details, headers, retry_after)
    if status_code >= 500:
        return ServerError(message, status_code, details, headers)
    return ValstormHttpError(message, status_code, details, headers)
