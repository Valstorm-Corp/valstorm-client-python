"""Query domain facades with exact 1:1 parity with PlatformContext.query."""

from typing import Any

from valstorm.facades.base import AsyncBaseFacade, SyncBaseFacade


class SyncQueryFacade(SyncBaseFacade):
    """Synchronous facade for SQL and GraphQL query execution."""

    def sql(
        self,
        query: str,
        limit: int | None = None,
        hydrate: bool = False,
        bypass_cache: bool = False,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        payload = {
            "query": query,
            "limit": limit or 50,
            "hydrate": hydrate,
            "bypass_cache": bypass_cache,
            **kwargs,
        }
        res = self._transport.request("POST", "query", json=payload)
        return res.data if isinstance(res.data, list) else []

    def graphql(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name
        res = self._transport.request("POST", "graphql", json=payload)
        return res.data if isinstance(res.data, dict) else {}


class AsyncQueryFacade(AsyncBaseFacade):
    """Asynchronous facade for SQL and GraphQL query execution."""

    async def sql(
        self,
        query: str,
        limit: int | None = None,
        hydrate: bool = False,
        bypass_cache: bool = False,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        payload = {
            "query": query,
            "limit": limit or 50,
            "hydrate": hydrate,
            "bypass_cache": bypass_cache,
            **kwargs,
        }
        res = await self._transport.request("POST", "query", json=payload)
        return res.data if isinstance(res.data, list) else []

    async def graphql(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name
        res = await self._transport.request("POST", "graphql", json=payload)
        return res.data if isinstance(res.data, dict) else {}
