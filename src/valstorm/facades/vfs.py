"""Virtual File Service (VFS) domain facades with exact 1:1 parity with PlatformContext.vfs."""

from typing import Any

from valstorm.facades.base import AsyncBaseFacade, SyncBaseFacade


class SyncVfsFacade(SyncBaseFacade):
    """Synchronous facade for Virtual File Service operations."""

    def tree(self) -> list[dict[str, Any]]:
        res = self._transport.request("GET", "vfs/tree")
        return res.data if isinstance(res.data, list) else []

    def snapshot(self, bypass_cache: bool = False) -> dict[str, Any]:
        res = self._transport.request("GET", "vfs/snapshot", params={"bypass_cache": bypass_cache})
        return res.data if isinstance(res.data, dict) else {}

    def get_vault(self, vault_id: str) -> dict[str, Any]:
        res = self._transport.request("GET", f"vfs/vault/{vault_id}")
        return res.data if isinstance(res.data, dict) else {}

    def resolve_path(self, path: str) -> dict[str, Any]:
        clean_path = path.strip("/")
        res = self._transport.request("GET", f"vfs/path/{clean_path}")
        return res.data if isinstance(res.data, dict) else {}

    def get_file_details(self, file_id: str) -> dict[str, Any]:
        res = self._transport.request("GET", f"vfs/file/{file_id}")
        return res.data if isinstance(res.data, dict) else {}

    def download_file_attachment(self, file_id: str) -> bytes:
        res = self._transport.request("GET", f"vfs/download/{file_id}")
        if isinstance(res.data, bytes):
            return res.data
        if isinstance(res.data, str):
            return res.data.encode("utf-8")
        return b""

    def move(
        self,
        item_id: str,
        from_vault_id: str | None = None,
        to_vault_id: str | None = None,
    ) -> dict[str, Any]:
        payload = {"item_id": item_id, "from_vault_id": from_vault_id, "to_vault_id": to_vault_id}
        res = self._transport.request("POST", "vfs/move", json=payload)
        return res.data if isinstance(res.data, dict) else {}

    def batch_move(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        res = self._transport.request("POST", "vfs/batch-move", json={"items": items})
        return res.data if isinstance(res.data, dict) else {}

    def delete(self, item_id: str) -> bool:
        self._transport.request("DELETE", f"vfs/item/{item_id}")
        return True

    def batch_delete(self, items: list[str]) -> bool:
        self._transport.request("POST", "vfs/batch-delete", json={"items": items})
        return True


class AsyncVfsFacade(AsyncBaseFacade):
    """Asynchronous facade for Virtual File Service operations."""

    async def tree(self) -> list[dict[str, Any]]:
        res = await self._transport.request("GET", "vfs/tree")
        return res.data if isinstance(res.data, list) else []

    async def snapshot(self, bypass_cache: bool = False) -> dict[str, Any]:
        res = await self._transport.request(
            "GET", "vfs/snapshot", params={"bypass_cache": bypass_cache}
        )
        return res.data if isinstance(res.data, dict) else {}

    async def get_vault(self, vault_id: str) -> dict[str, Any]:
        res = await self._transport.request("GET", f"vfs/vault/{vault_id}")
        return res.data if isinstance(res.data, dict) else {}

    async def resolve_path(self, path: str) -> dict[str, Any]:
        clean_path = path.strip("/")
        res = await self._transport.request("GET", f"vfs/path/{clean_path}")
        return res.data if isinstance(res.data, dict) else {}

    async def get_file_details(self, file_id: str) -> dict[str, Any]:
        res = await self._transport.request("GET", f"vfs/file/{file_id}")
        return res.data if isinstance(res.data, dict) else {}

    async def download_file_attachment(self, file_id: str) -> bytes:
        res = await self._transport.request("GET", f"vfs/download/{file_id}")
        if isinstance(res.data, bytes):
            return res.data
        if isinstance(res.data, str):
            return res.data.encode("utf-8")
        return b""

    async def move(
        self,
        item_id: str,
        from_vault_id: str | None = None,
        to_vault_id: str | None = None,
    ) -> dict[str, Any]:
        payload = {"item_id": item_id, "from_vault_id": from_vault_id, "to_vault_id": to_vault_id}
        res = await self._transport.request("POST", "vfs/move", json=payload)
        return res.data if isinstance(res.data, dict) else {}

    async def batch_move(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        res = await self._transport.request("POST", "vfs/batch-move", json={"items": items})
        return res.data if isinstance(res.data, dict) else {}

    async def delete(self, item_id: str) -> bool:
        await self._transport.request("DELETE", f"vfs/item/{item_id}")
        return True

    async def batch_delete(self, items: list[str]) -> bool:
        await self._transport.request("POST", "vfs/batch-delete", json={"items": items})
        return True
