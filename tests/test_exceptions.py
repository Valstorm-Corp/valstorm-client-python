"""Tests for HTTP exception mapping and error payloads."""

from valstorm.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
    ValstormHttpError,
    map_http_status_to_exception,
)


def test_exception_mapping_401():
    exc = map_http_status_to_exception(401, "Invalid token")
    assert isinstance(exc, AuthenticationError)
    assert exc.status_code == 401
    assert exc.message == "Invalid token"


def test_exception_mapping_403():
    exc = map_http_status_to_exception(403, "Forbidden")
    assert isinstance(exc, PermissionDeniedError)
    assert exc.status_code == 403


def test_exception_mapping_404():
    exc = map_http_status_to_exception(404, "Not found")
    assert isinstance(exc, NotFoundError)
    assert exc.status_code == 404


def test_exception_mapping_409():
    exc = map_http_status_to_exception(409, "Record conflict")
    assert isinstance(exc, ConflictError)
    assert exc.status_code == 409


def test_exception_mapping_422():
    exc = map_http_status_to_exception(
        422, "Validation failed", details={"errors": [{"field": "email"}]}
    )
    assert isinstance(exc, ValidationError)
    assert exc.status_code == 422
    assert exc.details == {"errors": [{"field": "email"}]}


def test_exception_mapping_429():
    headers = {"Retry-After": "12.5"}
    exc = map_http_status_to_exception(429, "Too many requests", headers=headers)
    assert isinstance(exc, RateLimitError)
    assert exc.status_code == 429
    assert exc.retry_after == 12.5


def test_exception_mapping_500():
    exc = map_http_status_to_exception(500, "Internal Server Error")
    assert isinstance(exc, ServerError)
    assert exc.status_code == 500


def test_exception_mapping_unknown():
    exc = map_http_status_to_exception(418, "I'm a teapot")
    assert isinstance(exc, ValstormHttpError)
    assert exc.status_code == 418
