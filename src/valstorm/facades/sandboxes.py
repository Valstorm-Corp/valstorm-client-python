"""Sandbox domain facades with exact 1:1 parity with PlatformContext.sandboxes."""

from typing import Any

from valstorm.facades.base import AsyncBaseFacade, SyncBaseFacade


class SyncSandboxFacade(SyncBaseFacade):
    """Synchronous facade for organization sandbox operations."""

    def create(self, name: str, description: str | None = None) -> dict[str, Any]:
        payload = {"name": name, "description": description}
        res = self._transport.request("POST", "sandboxes", json=payload)
        return res.data if isinstance(res.data, dict) else {}

    def delete(self, sandbox_id: str) -> bool:
        self._transport.request("DELETE", f"sandboxes/{sandbox_id}")
        return True


class AsyncSandboxFacade(AsyncBaseFacade):
    """Asynchronous facade for organization sandbox operations."""

    async def create(self, name: str, description: str | None = None) -> dict[str, Any]:
        payload = {"name": name, "description": description}
        res = await self._transport.request("POST", "sandboxes", json=payload)
        return res.data if isinstance(res.data, dict) else {}

    async def delete(self, sandbox_id: str) -> bool:
        await self._transport.request("DELETE", f"sandboxes/{sandbox_id}")
        return True
