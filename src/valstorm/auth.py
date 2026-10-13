"""Authentication strategies and token lifecycle management for Valstorm Client SDK."""

import asyncio
import base64
import json
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import httpx


def decode_jwt_unverified(token: str) -> dict[str, Any]:
    """Decodes JWT payload without cryptographic verification to check claims and exp."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        payload_b64 = parts[1]
        padding = len(payload_b64) % 4
        if padding:
            payload_b64 += "=" * (4 - padding)
        payload_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        return {}


def is_jwt_expiring(token: str, margin_seconds: int = 60) -> bool:
    """Returns True if the token is an expired or expiring JWT."""
    payload = decode_jwt_unverified(token)
    if not payload or "exp" not in payload:
        return False
    try:
        exp = float(payload["exp"])
        return time.time() >= (exp - margin_seconds)
    except (ValueError, TypeError):
        return False


class AuthProvider(ABC):
    """Abstract base class for all authentication providers."""

    @abstractmethod
    def get_auth_headers(self) -> dict[str, str]:
        """Returns the authentication headers for synchronous requests."""

    @abstractmethod
    async def get_auth_headers_async(self) -> dict[str, str]:
        """Returns the authentication headers for asynchronous requests."""

    def handle_unauthorized(self, base_url: str, http_client: httpx.Client) -> bool:
        """Handles 401 Unauthorized for synchronous requests. Returns True if refreshed."""
        return False

    async def handle_unauthorized_async(
        self, base_url: str, http_client: httpx.AsyncClient
    ) -> bool:
        """Handles 401 Unauthorized for asynchronous requests. Returns True if refreshed."""
        return False


class PatAuth(AuthProvider):
    """Personal Access Token (PAT) authentication strategy."""

    def __init__(self, token: str):
        if not token:
            raise ValueError("Token must not be empty")
        self.token = token.strip()

    def get_auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}

    async def get_auth_headers_async(self) -> dict[str, str]:
        return self.get_auth_headers()


class ServiceKeyAuth(AuthProvider):
    """Machine-to-Machine (M2M) Service Key authentication strategy."""

    def __init__(self, service_key: str, organization_id: str | None = None):
        if not service_key:
            raise ValueError("Service key must not be empty")
        self.service_key = service_key.strip()
        self.organization_id = organization_id

    def get_auth_headers(self) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {self.service_key}"}
        if self.organization_id:
            headers["X-Organization-ID"] = self.organization_id
        return headers

    async def get_auth_headers_async(self) -> dict[str, str]:
        return self.get_auth_headers()


class UserJwtAuth(AuthProvider):
    """
    Interactive User OAuth2 JWT authentication strategy.
    Supports proactive expiration detection and reactive 401 auto-refresh with mutex locking.
    """

    def __init__(
        self,
        access_token: str,
        refresh_token: str | None = None,
        on_refresh: Callable[[str, str | None], Any] | None = None,
        refresh_path: str = "/oauth2/refresh",
    ):
        if not access_token:
            raise ValueError("Access token must not be empty")
        self.access_token = access_token.strip()
        self.refresh_token = refresh_token.strip() if refresh_token else None
        self.on_refresh = on_refresh
        self.refresh_path = refresh_path
        self._sync_lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    def _resolve_refresh_url(self, base_url: str) -> str:
        clean = base_url.rstrip("/")
        path = self.refresh_path.lstrip("/")
        if not clean.endswith("/v1") and not path.startswith("v1/"):
            return f"{clean}/v1/{path}"
        return f"{clean}/{path}"

    def get_auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

    async def get_auth_headers_async(self) -> dict[str, str]:
        return self.get_auth_headers()

    def refresh(self, base_url: str, http_client: httpx.Client | None = None) -> bool:
        """Synchronously refreshes the access token using the refresh token."""
        if not self.refresh_token:
            return False

        with self._sync_lock:
            refresh_url = self._resolve_refresh_url(base_url)
            client = http_client or httpx.Client(timeout=15.0)
            try:
                res = client.post(
                    refresh_url,
                    json={"refresh_token": self.refresh_token},
                    headers={"Content-Type": "application/json"},
                )
                if res.is_success:
                    data = res.json()
                    new_access = data.get("access_token") or data.get("token")
                    if new_access:
                        self.access_token = new_access
                        new_refresh = data.get("refresh_token")
                        if new_refresh:
                            self.refresh_token = new_refresh
                        if self.on_refresh:
                            self.on_refresh(self.access_token, self.refresh_token)
                        return True
                return False
            except Exception:
                return False
            finally:
                if http_client is None:
                    client.close()

    async def refresh_async(
        self, base_url: str, http_client: httpx.AsyncClient | None = None
    ) -> bool:
        """Asynchronously refreshes the access token using the refresh token."""
        if not self.refresh_token:
            return False

        async with self._async_lock:
            refresh_url = self._resolve_refresh_url(base_url)
            client = http_client or httpx.AsyncClient(timeout=15.0)
            try:
                res = await client.post(
                    refresh_url,
                    json={"refresh_token": self.refresh_token},
                    headers={"Content-Type": "application/json"},
                )
                if res.is_success:
                    data = res.json()
                    new_access = data.get("access_token") or data.get("token")
                    if new_access:
                        self.access_token = new_access
                        new_refresh = data.get("refresh_token")
                        if new_refresh:
                            self.refresh_token = new_refresh
                        if self.on_refresh:
                            cb_res = self.on_refresh(self.access_token, self.refresh_token)
                            if asyncio.iscoroutine(cb_res):
                                await cb_res
                        return True
                return False
            except Exception:
                return False
            finally:
                if http_client is None:
                    await client.aclose()

    def handle_unauthorized(self, base_url: str, http_client: httpx.Client) -> bool:
        return self.refresh(base_url=base_url, http_client=http_client)

    async def handle_unauthorized_async(
        self, base_url: str, http_client: httpx.AsyncClient
    ) -> bool:
        return await self.refresh_async(base_url=base_url, http_client=http_client)
