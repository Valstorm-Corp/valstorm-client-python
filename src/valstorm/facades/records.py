"""Record domain facades with exact 1:1 parity with PlatformContext.records."""

from typing import Any

from valstorm.exceptions import NotFoundError
from valstorm.facades.base import AsyncBaseFacade, SyncBaseFacade


class SyncRecordFacade(SyncBaseFacade):
    """Synchronous facade for record operations."""

    def create(
        self,
        api_name: str,
        records: dict[str, Any] | list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        payload = [records] if isinstance(records, dict) else records
        res = self._transport.request("POST", f"object/{api_name}", json=payload)
        return res.data if isinstance(res.data, list) else [res.data]

    def update(
        self,
        api_name: str,
        records: dict[str, Any] | list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        payload = [records] if isinstance(records, dict) else records
        res = self._transport.request("PATCH", f"object/{api_name}", json=payload)
        return res.data if isinstance(res.data, list) else [res.data]

    def delete(
        self,
        api_name: str,
        ids: str | list[str],
    ) -> int:
        if isinstance(ids, str):
            self._transport.request("DELETE", f"object/{api_name}/{ids}")
            return 1
        id_str = ",".join(ids)
        self._transport.request("DELETE", f"object/{api_name}", params={"ids": id_str})
        return len(ids)

    def get(
        self,
        api_name: str,
        record_id: str,
    ) -> dict[str, Any] | None:
        try:
            res = self._transport.request("GET", f"object/{api_name}/{record_id}")
            return res.data
        except NotFoundError:
            return None

    def list(
        self,
        api_name: str,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "created_date DESC",
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        params: dict[str, Any] = {"limit": limit, "offset": offset, "order_by": order_by}
        if filters:
            for k, v in filters.items():
                params[f"filter_{k}"] = v
        res = self._transport.request("GET", f"object/{api_name}", params=params)
        records = res.data if isinstance(res.data, list) else []
        total = res.total_count if res.total_count is not None else len(records)
        return records, total


class AsyncRecordFacade(AsyncBaseFacade):
    """Asynchronous facade for record operations."""

    async def create(
        self,
        api_name: str,
        records: dict[str, Any] | list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        payload = [records] if isinstance(records, dict) else records
        res = await self._transport.request("POST", f"object/{api_name}", json=payload)
        return res.data if isinstance(res.data, list) else [res.data]

    async def update(
        self,
        api_name: str,
        records: dict[str, Any] | list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        payload = [records] if isinstance(records, dict) else records
        res = await self._transport.request("PATCH", f"object/{api_name}", json=payload)
        return res.data if isinstance(res.data, list) else [res.data]

    async def delete(
        self,
        api_name: str,
        ids: str | list[str],
    ) -> int:
        if isinstance(ids, str):
            await self._transport.request("DELETE", f"object/{api_name}/{ids}")
            return 1
        id_str = ",".join(ids)
        await self._transport.request("DELETE", f"object/{api_name}", params={"ids": id_str})
        return len(ids)

    async def get(
        self,
        api_name: str,
        record_id: str,
    ) -> dict[str, Any] | None:
        try:
            res = await self._transport.request("GET", f"object/{api_name}/{record_id}")
            return res.data
        except NotFoundError:
            return None

    async def list(
        self,
        api_name: str,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "created_date DESC",
        filters: dict[str, Any] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        params: dict[str, Any] = {"limit": limit, "offset": offset, "order_by": order_by}
        if filters:
            for k, v in filters.items():
                params[f"filter_{k}"] = v
        res = await self._transport.request("GET", f"object/{api_name}", params=params)
        records = res.data if isinstance(res.data, list) else []
        total = res.total_count if res.total_count is not None else len(records)
        return records, total
