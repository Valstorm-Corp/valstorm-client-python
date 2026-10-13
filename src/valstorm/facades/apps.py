"""Apps domain facades with exact 1:1 parity with PlatformContext.apps."""

from typing import Any

from valstorm.facades.base import AsyncBaseFacade, SyncBaseFacade


class SyncAppFacade(SyncBaseFacade):
    """Synchronous facade for modular application and marketplace operations."""

    def list_installed(self) -> list[dict[str, Any]]:
        res = self._transport.request("GET", "apps")
        return res.data if isinstance(res.data, list) else []

    def list_marketplace(self) -> list[dict[str, Any]]:
        try:
            res = self._transport.request("GET", "apps/marketplace")
        except Exception:
            res = self._transport.request("GET", "apps", params={"marketplace": "true"})
        return res.data if isinstance(res.data, list) else []

    def get(self, app_id: str) -> dict[str, Any] | None:
        res = self._transport.request("GET", f"apps/{app_id}")
        return res.data if isinstance(res.data, dict) else None

    def install(self, app_id: str) -> dict[str, Any]:
        try:
            res = self._transport.request("POST", f"apps/install/{app_id}")
        except Exception:
            res = self._transport.request("POST", "apps/apply-apps", json={"app_ids": [app_id]})
        return res.data if isinstance(res.data, dict) else {}

    def bulk_install(self, app_ids: list[str]) -> dict[str, Any]:
        res = self._transport.request("POST", "apps/apply-apps", json={"app_ids": app_ids})
        return res.data if isinstance(res.data, dict) else {}

    def deploy(self, bundle: dict[str, Any]) -> dict[str, Any]:
        res = self._transport.request("PUT", "apps/deploy", json=bundle)
        return res.data if isinstance(res.data, dict) else {}


class AsyncAppFacade(AsyncBaseFacade):
    """Asynchronous facade for modular application and marketplace operations."""

    async def list_installed(self) -> list[dict[str, Any]]:
        res = await self._transport.request("GET", "apps")
        return res.data if isinstance(res.data, list) else []

    async def list_marketplace(self) -> list[dict[str, Any]]:
        try:
            res = await self._transport.request("GET", "apps/marketplace")
        except Exception:
            res = await self._transport.request("GET", "apps", params={"marketplace": "true"})
        return res.data if isinstance(res.data, list) else []

    async def get(self, app_id: str) -> dict[str, Any] | None:
        res = await self._transport.request("GET", f"apps/{app_id}")
        return res.data if isinstance(res.data, dict) else None

    async def install(self, app_id: str) -> dict[str, Any]:
        try:
            res = await self._transport.request("POST", f"apps/install/{app_id}")
        except Exception:
            res = await self._transport.request(
                "POST", "apps/apply-apps", json={"app_ids": [app_id]}
            )
        return res.data if isinstance(res.data, dict) else {}

    async def bulk_install(self, app_ids: list[str]) -> dict[str, Any]:
        res = await self._transport.request("POST", "apps/apply-apps", json={"app_ids": app_ids})
        return res.data if isinstance(res.data, dict) else {}

    async def deploy(self, bundle: dict[str, Any]) -> dict[str, Any]:
        res = await self._transport.request("PUT", "apps/deploy", json=bundle)
        return res.data if isinstance(res.data, dict) else {}
