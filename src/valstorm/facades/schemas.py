"""Schema domain facades with exact 1:1 parity with PlatformContext.schemas."""

from typing import Any

from valstorm.facades.base import AsyncBaseFacade, SyncBaseFacade


class SyncSchemaFacade(SyncBaseFacade):
    """Synchronous facade for schema operations."""

    def list(self) -> dict[str, Any]:
        res = self._transport.request("GET", "schema")
        return res.data if isinstance(res.data, dict) else {}

    def get(self, api_name: str) -> dict[str, Any]:
        res = self._transport.request("GET", f"schema/{api_name}")
        return res.data if isinstance(res.data, dict) else {}

    def create(self, schema_data: dict[str, Any]) -> dict[str, Any]:
        res = self._transport.request("POST", "schema", json=schema_data)
        return res.data if isinstance(res.data, dict) else {}

    def update(self, schema_data: dict[str, Any]) -> dict[str, Any]:
        res = self._transport.request("PATCH", "schema", json=schema_data)
        return res.data if isinstance(res.data, dict) else {}

    def delete(self, api_name: str) -> bool:
        self._transport.request("DELETE", f"schema/{api_name}")
        return True

    def add_field(self, api_name: str, field_data: dict[str, Any]) -> dict[str, Any]:
        payload = {"object_name": api_name, "field": field_data}
        res = self._transport.request("POST", "schema/field", json=payload)
        return res.data if isinstance(res.data, dict) else {}

    def delete_field(self, api_name: str, field_name: str) -> bool:
        self._transport.request("DELETE", f"schema/{api_name}/{field_name}")
        return True


class AsyncSchemaFacade(AsyncBaseFacade):
    """Asynchronous facade for schema operations."""

    async def list(self) -> dict[str, Any]:
        res = await self._transport.request("GET", "schema")
        return res.data if isinstance(res.data, dict) else {}

    async def get(self, api_name: str) -> dict[str, Any]:
        res = await self._transport.request("GET", f"schema/{api_name}")
        return res.data if isinstance(res.data, dict) else {}

    async def create(self, schema_data: dict[str, Any]) -> dict[str, Any]:
        res = await self._transport.request("POST", "schema", json=schema_data)
        return res.data if isinstance(res.data, dict) else {}

    async def update(self, schema_data: dict[str, Any]) -> dict[str, Any]:
        res = await self._transport.request("PATCH", "schema", json=schema_data)
        return res.data if isinstance(res.data, dict) else {}

    async def delete(self, api_name: str) -> bool:
        await self._transport.request("DELETE", f"schema/{api_name}")
        return True

    async def add_field(self, api_name: str, field_data: dict[str, Any]) -> dict[str, Any]:
        payload = {"object_name": api_name, "field": field_data}
        res = await self._transport.request("POST", "schema/field", json=payload)
        return res.data if isinstance(res.data, dict) else {}

    async def delete_field(self, api_name: str, field_name: str) -> bool:
        await self._transport.request("DELETE", f"schema/{api_name}/{field_name}")
        return True
