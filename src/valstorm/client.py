"""Main client entry points for Valstorm SDK providing 1:1 parity with PlatformContext."""

import os
from typing import Any

import httpx

from valstorm.auth import AuthProvider, PatAuth, ServiceKeyAuth, UserJwtAuth
from valstorm.facades.apps import AsyncAppFacade, SyncAppFacade
from valstorm.facades.files import AsyncFileFacade, SyncFileFacade
from valstorm.facades.query import AsyncQueryFacade, SyncQueryFacade
from valstorm.facades.records import AsyncRecordFacade, SyncRecordFacade
from valstorm.facades.sandboxes import AsyncSandboxFacade, SyncSandboxFacade
from valstorm.facades.schemas import AsyncSchemaFacade, SyncSchemaFacade
from valstorm.facades.vfs import AsyncVfsFacade, SyncVfsFacade
from valstorm.transport import AsyncTransport, SyncTransport

DEFAULT_API_URL = "http://localhost:8010/v1"


def _resolve_auth(
    auth: AuthProvider | str | None = None,
    api_key: str | None = None,
    token: str | None = None,
    service_key: str | None = None,
    organization_id: str | None = None,
) -> AuthProvider:
    """Resolves authentication provider from explicit auth instance, keys, or env vars."""
    if isinstance(auth, AuthProvider):
        return auth
    if isinstance(auth, str):
        token_str = auth.strip()
        if token_str.startswith("vst_sk_"):
            return ServiceKeyAuth(token_str, organization_id=organization_id)
        if token_str.startswith("vst_pat_"):
            return PatAuth(token_str)
        return UserJwtAuth(token_str)

    if api_key:
        return PatAuth(api_key)
    if service_key:
        return ServiceKeyAuth(service_key, organization_id=organization_id)
    if token:
        return UserJwtAuth(token)

    # Check environment variables
    env_key = os.getenv("VALSTORM_API_KEY") or os.getenv("VALSTORM_PAT")
    if env_key:
        return PatAuth(env_key)

    env_sk = os.getenv("VALSTORM_SERVICE_KEY")
    if env_sk:
        return ServiceKeyAuth(env_sk, organization_id=os.getenv("VALSTORM_ORG_ID"))

    env_token = os.getenv("VALSTORM_TOKEN") or os.getenv("VALSTORM_ACCESS_TOKEN")
    if env_token:
        refresh = os.getenv("VALSTORM_REFRESH_TOKEN")
        return UserJwtAuth(env_token, refresh_token=refresh)

    raise ValueError(
        "No authentication provided. Provide an AuthProvider instance, api_key, token, "
        "or set VALSTORM_API_KEY / VALSTORM_TOKEN in your environment."
    )


class BaseValstormClient:
    """Base client holding configuration and shared state."""

    def __init__(
        self,
        base_url: str | None = None,
        auth: AuthProvider | str | None = None,
        api_key: str | None = None,
        token: str | None = None,
        service_key: str | None = None,
        organization_id: str | None = None,
        timeout: float = 30.0,
        default_headers: dict[str, str] | None = None,
    ):
        self.base_url = (
            base_url
            or os.getenv("VALSTORM_BASE_URL")
            or os.getenv("VALSTORM_API_URL")
            or DEFAULT_API_URL
        ).rstrip("/")
        self.auth = _resolve_auth(
            auth=auth,
            api_key=api_key,
            token=token,
            service_key=service_key,
            organization_id=organization_id or os.getenv("VALSTORM_ORG_ID"),
        )
        self.timeout = timeout
        self.default_headers = default_headers or {}


class ValstormClient(BaseValstormClient):
    """
    Synchronous Valstorm Client SDK.
    Provides exact 1:1 domain facade parity with server-side PlatformContext:
      - client.records.*
      - client.query.*
      - client.schemas.*
      - client.vfs.*
      - client.files.*
      - client.apps.*
      - client.sandboxes.*
    """

    def __init__(
        self,
        base_url: str | None = None,
        auth: AuthProvider | str | None = None,
        api_key: str | None = None,
        token: str | None = None,
        service_key: str | None = None,
        organization_id: str | None = None,
        timeout: float = 30.0,
        default_headers: dict[str, str] | None = None,
        http_client: httpx.Client | None = None,
    ):
        super().__init__(
            base_url=base_url,
            auth=auth,
            api_key=api_key,
            token=token,
            service_key=service_key,
            organization_id=organization_id,
            timeout=timeout,
            default_headers=default_headers,
        )
        self._transport = SyncTransport(
            base_url=self.base_url,
            auth=self.auth,
            timeout=self.timeout,
            default_headers=self.default_headers,
            client=http_client,
        )

        # Domain Facades (1:1 parity with PlatformContext)
        self.records = SyncRecordFacade(self)
        self.query = SyncQueryFacade(self)
        self.schemas = SyncSchemaFacade(self)
        self.vfs = SyncVfsFacade(self)
        self.files = SyncFileFacade(self)
        self.apps = SyncAppFacade(self)
        self.sandboxes = SyncSandboxFacade(self)

    @classmethod
    def from_env(cls, **kwargs: Any) -> "ValstormClient":
        """Instantiates client automatically using environment variables."""
        return cls(**kwargs)

    @property
    def transport(self) -> SyncTransport:
        return self._transport

    def close(self) -> None:
        """Closes the underlying HTTP transport."""
        self._transport.close()

    def __enter__(self) -> "ValstormClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


class AsyncValstormClient(BaseValstormClient):
    """
    Asynchronous Valstorm Client SDK.
    Provides exact 1:1 domain facade parity with server-side PlatformContext:
      - await client.records.*
      - await client.query.*
      - await client.schemas.*
      - await client.vfs.*
      - await client.files.*
      - await client.apps.*
      - await client.sandboxes.*
    """

    def __init__(
        self,
        base_url: str | None = None,
        auth: AuthProvider | str | None = None,
        api_key: str | None = None,
        token: str | None = None,
        service_key: str | None = None,
        organization_id: str | None = None,
        timeout: float = 30.0,
        default_headers: dict[str, str] | None = None,
        http_client: httpx.AsyncClient | None = None,
    ):
        super().__init__(
            base_url=base_url,
            auth=auth,
            api_key=api_key,
            token=token,
            service_key=service_key,
            organization_id=organization_id,
            timeout=timeout,
            default_headers=default_headers,
        )
        self._transport = AsyncTransport(
            base_url=self.base_url,
            auth=self.auth,
            timeout=self.timeout,
            default_headers=self.default_headers,
            client=http_client,
        )

        # Domain Facades (1:1 parity with PlatformContext)
        self.records = AsyncRecordFacade(self)
        self.query = AsyncQueryFacade(self)
        self.schemas = AsyncSchemaFacade(self)
        self.vfs = AsyncVfsFacade(self)
        self.files = AsyncFileFacade(self)
        self.apps = AsyncAppFacade(self)
        self.sandboxes = AsyncSandboxFacade(self)

    @classmethod
    def from_env(cls, **kwargs: Any) -> "AsyncValstormClient":
        """Instantiates async client automatically using environment variables."""
        return cls(**kwargs)

    @property
    def transport(self) -> AsyncTransport:
        return self._transport

    async def aclose(self) -> None:
        """Closes the underlying async HTTP transport."""
        await self._transport.aclose()

    async def __aenter__(self) -> "AsyncValstormClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.aclose()
