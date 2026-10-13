"""Official Python Client SDK for Open Valstorm."""

from valstorm.auth import (
    AuthProvider,
    PatAuth,
    ServiceKeyAuth,
    UserJwtAuth,
    decode_jwt_unverified,
    is_jwt_expiring,
)
from valstorm.client import AsyncValstormClient, ValstormClient
from valstorm.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    RequestTimeoutError,
    ServerError,
    TransportError,
    ValidationError,
    ValstormError,
    ValstormHttpError,
)
from valstorm.protocols import (
    AppOperations,
    FileOperations,
    PlatformProtocol,
    QueryOperations,
    RecordOperations,
    SandboxOperations,
    SchemaOperations,
    VfsOperations,
)
from valstorm.version import __version__

__all__ = [
    # Clients
    "ValstormClient",
    "AsyncValstormClient",
    # Auth
    "AuthProvider",
    "PatAuth",
    "ServiceKeyAuth",
    "UserJwtAuth",
    "decode_jwt_unverified",
    "is_jwt_expiring",
    # Exceptions
    "ValstormError",
    "ValstormHttpError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "TransportError",
    "RequestTimeoutError",
    # Protocols
    "PlatformProtocol",
    "RecordOperations",
    "QueryOperations",
    "SchemaOperations",
    "VfsOperations",
    "FileOperations",
    "AppOperations",
    "SandboxOperations",
    # Metadata
    "__version__",
]
