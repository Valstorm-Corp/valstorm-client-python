"""HTTP transport management with retry, tracing, and unified response evaluation."""

import uuid
from typing import Any

import httpx

from valstorm.auth import AuthProvider
from valstorm.exceptions import (
    RequestTimeoutError,
    TransportError,
    map_http_status_to_exception,
)
from valstorm.version import __version__

DEFAULT_USER_AGENT = f"Valstorm-Client-Python/{__version__}"


class TransportResponse:
    """Wrapper around response data and pagination metadata."""

    def __init__(self, data: Any, status_code: int, headers: dict[str, str]):
        self.data = data
        self.status_code = status_code
        self.headers = headers

    @property
    def total_count(self) -> int | None:
        total = self.headers.get("x-total-count") or self.headers.get("X-Total-Count")
        if total is not None:
            try:
                return int(total)
            except (ValueError, TypeError):
                pass
        return None


class BaseTransport:
    """Shared HTTP serialization, header preparation, and response decoding."""

    def __init__(
        self,
        base_url: str,
        auth: AuthProvider,
        timeout: float = 30.0,
        default_headers: dict[str, str] | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.timeout = timeout
        self.default_headers = default_headers or {}

    def _build_url(self, path: str) -> str:
        clean_path = path.lstrip("/")
        # If path does not start with v1/ and base_url doesn't end with /v1, prefix with /v1
        if not clean_path.startswith("v1/") and not self.base_url.endswith("/v1"):
            clean_path = f"v1/{clean_path}"
        return f"{self.base_url}/{clean_path}"

    def _prepare_headers(
        self,
        auth_headers: dict[str, str],
        custom_headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": DEFAULT_USER_AGENT,
            "X-Request-ID": f"req_{uuid.uuid4().hex[:16]}",
        }
        headers.update(self.default_headers)
        headers.update(auth_headers)
        if custom_headers:
            headers.update(custom_headers)
        return headers

    def _process_response(self, response: httpx.Response) -> TransportResponse:
        headers_dict = dict(response.headers)
        if response.is_success:
            if response.status_code == 204:
                return TransportResponse(None, response.status_code, headers_dict)
            try:
                data = response.json()
            except Exception:
                data = response.text
            return TransportResponse(data, response.status_code, headers_dict)

        # Parse error message & details
        try:
            body = response.json()
            if isinstance(body, dict):
                msg = body.get("detail") or body.get("message") or str(body)
                details = body
            else:
                msg = str(body)
                details = body
        except Exception:
            msg = response.text or f"HTTP Error {response.status_code}"
            details = None

        raise map_http_status_to_exception(
            status_code=response.status_code,
            message=str(msg),
            details=details,
            headers=headers_dict,
        )


def _has_h2() -> bool:
    try:
        import h2  # noqa: F401

        return True
    except ImportError:
        return False


class SyncTransport(BaseTransport):
    """Synchronous HTTP transport utilizing httpx.Client."""

    def __init__(
        self,
        base_url: str,
        auth: AuthProvider,
        timeout: float = 30.0,
        default_headers: dict[str, str] | None = None,
        client: httpx.Client | None = None,
    ):
        super().__init__(base_url, auth, timeout, default_headers)
        self.client = client or httpx.Client(
            timeout=timeout,
            http2=_has_h2(),
            follow_redirects=True,
        )
        self._owns_client = client is None

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> TransportResponse:
        url = self._build_url(path)
        auth_headers = self.auth.get_auth_headers()
        full_headers = self._prepare_headers(auth_headers, headers)

        try:
            res = self.client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=full_headers,
            )
            # Check for 401 auto-refresh retry
            if res.status_code == 401:
                refreshed = self.auth.handle_unauthorized(self.base_url, self.client)
                if refreshed:
                    new_auth = self.auth.get_auth_headers()
                    retry_headers = self._prepare_headers(new_auth, headers)
                    res = self.client.request(
                        method=method,
                        url=url,
                        params=params,
                        json=json,
                        data=data,
                        files=files,
                        headers=retry_headers,
                    )
            return self._process_response(res)
        except httpx.TimeoutException as e:
            raise RequestTimeoutError(f"Request timed out: {e}") from e
        except httpx.RequestError as e:
            raise TransportError(f"HTTP transport failed: {e}") from e

    def close(self) -> None:
        if self._owns_client:
            self.client.close()


class AsyncTransport(BaseTransport):
    """Asynchronous HTTP transport utilizing httpx.AsyncClient."""

    def __init__(
        self,
        base_url: str,
        auth: AuthProvider,
        timeout: float = 30.0,
        default_headers: dict[str, str] | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        super().__init__(base_url, auth, timeout, default_headers)
        self.client = client or httpx.AsyncClient(
            timeout=timeout,
            http2=_has_h2(),
            follow_redirects=True,
        )
        self._owns_client = client is None

    async def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> TransportResponse:
        url = self._build_url(path)
        auth_headers = await self.auth.get_auth_headers_async()
        full_headers = self._prepare_headers(auth_headers, headers)

        try:
            res = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                files=files,
                headers=full_headers,
            )
            # Check for 401 auto-refresh retry
            if res.status_code == 401:
                refreshed = await self.auth.handle_unauthorized_async(self.base_url, self.client)
                if refreshed:
                    new_auth = await self.auth.get_auth_headers_async()
                    retry_headers = self._prepare_headers(new_auth, headers)
                    res = await self.client.request(
                        method=method,
                        url=url,
                        params=params,
                        json=json,
                        data=data,
                        files=files,
                        headers=retry_headers,
                    )
            return self._process_response(res)
        except httpx.TimeoutException as e:
            raise RequestTimeoutError(f"Request timed out: {e}") from e
        except httpx.RequestError as e:
            raise TransportError(f"HTTP transport failed: {e}") from e

    async def aclose(self) -> None:
        if self._owns_client:
            await self.client.aclose()
