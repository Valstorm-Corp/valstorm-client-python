"""Files domain facades with exact 1:1 parity with PlatformContext.files."""

from typing import Any

from valstorm.facades.base import AsyncBaseFacade, SyncBaseFacade


class SyncFileFacade(SyncBaseFacade):
    """Synchronous facade for file storage operations."""

    def get(self, file_id: str) -> dict[str, Any]:
        res = self._transport.request("GET", f"files/{file_id}")
        return res.data if isinstance(res.data, dict) else {}

    def register(self, file_data: dict[str, Any]) -> dict[str, Any]:
        res = self._transport.request("POST", "files/register", json=file_data)
        return res.data if isinstance(res.data, dict) else {}

    def save_content(self, file_id: str, content: str) -> dict[str, Any]:
        res = self._transport.request("POST", f"files/{file_id}/content", json={"content": content})
        return res.data if isinstance(res.data, dict) else {}

    def presigned_upload(
        self,
        filename: str,
        mime_type: str = "application/octet-stream",
        vault_id: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "filename": filename,
            "content_type": mime_type,
            "mime_type": mime_type,
            "vaults": [vault_id] if vault_id else None,
            "vault_id": vault_id,
        }
        res = self._transport.request("POST", "files/presigned-upload", json=payload)
        return res.data if isinstance(res.data, dict) else {}

    def direct_upload(
        self,
        filename: str,
        content: bytes,
        mime_type: str | None = None,
        vault_id: str | None = None,
    ) -> dict[str, Any]:
        files = {"file": (filename, content, mime_type or "application/octet-stream")}
        data = {"vaults": f'["{vault_id}"]'} if vault_id else {}
        params = {"vault_id": vault_id} if vault_id else None
        try:
            res = self._transport.request("POST", "files", files=files, data=data, params=params)
        except Exception:
            res = self._transport.request("PUT", "files/upload-direct", files=files, params=params)
        return res.data if isinstance(res.data, dict) else {}

    def get_versions(self, file_id: str) -> list[dict[str, Any]]:
        res = self._transport.request("GET", f"files/{file_id}/versions")
        return res.data if isinstance(res.data, list) else []

    def rollback(self, file_id: str, version_number: int) -> dict[str, Any]:
        payload = {"target_version": version_number, "version_number": version_number}
        res = self._transport.request("POST", f"files/{file_id}/rollback", json=payload)
        return res.data if isinstance(res.data, dict) else {}

    def delete(self, file_id: str) -> bool:
        self._transport.request("DELETE", f"files/{file_id}")
        return True


class AsyncFileFacade(AsyncBaseFacade):
    """Asynchronous facade for file storage operations."""

    async def get(self, file_id: str) -> dict[str, Any]:
        res = await self._transport.request("GET", f"files/{file_id}")
        return res.data if isinstance(res.data, dict) else {}

    async def register(self, file_data: dict[str, Any]) -> dict[str, Any]:
        res = await self._transport.request("POST", "files/register", json=file_data)
        return res.data if isinstance(res.data, dict) else {}

    async def save_content(self, file_id: str, content: str) -> dict[str, Any]:
        res = await self._transport.request(
            "POST", f"files/{file_id}/content", json={"content": content}
        )
        return res.data if isinstance(res.data, dict) else {}

    async def presigned_upload(
        self,
        filename: str,
        mime_type: str = "application/octet-stream",
        vault_id: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "filename": filename,
            "content_type": mime_type,
            "mime_type": mime_type,
            "vaults": [vault_id] if vault_id else None,
            "vault_id": vault_id,
        }
        res = await self._transport.request("POST", "files/presigned-upload", json=payload)
        return res.data if isinstance(res.data, dict) else {}

    async def direct_upload(
        self,
        filename: str,
        content: bytes,
        mime_type: str | None = None,
        vault_id: str | None = None,
    ) -> dict[str, Any]:
        files = {"file": (filename, content, mime_type or "application/octet-stream")}
        data = {"vaults": f'["{vault_id}"]'} if vault_id else {}
        params = {"vault_id": vault_id} if vault_id else None
        try:
            res = await self._transport.request(
                "POST", "files", files=files, data=data, params=params
            )
        except Exception:
            res = await self._transport.request(
                "PUT", "files/upload-direct", files=files, params=params
            )
        return res.data if isinstance(res.data, dict) else {}

    async def get_versions(self, file_id: str) -> list[dict[str, Any]]:
        res = await self._transport.request("GET", f"files/{file_id}/versions")
        return res.data if isinstance(res.data, list) else []

    async def rollback(self, file_id: str, version_number: int) -> dict[str, Any]:
        payload = {"target_version": version_number, "version_number": version_number}
        res = await self._transport.request("POST", f"files/{file_id}/rollback", json=payload)
        return res.data if isinstance(res.data, dict) else {}

    async def delete(self, file_id: str) -> bool:
        await self._transport.request("DELETE", f"files/{file_id}")
        return True
