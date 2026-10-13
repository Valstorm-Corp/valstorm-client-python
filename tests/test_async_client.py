"""Tests for asynchronous AsyncValstormClient and domain facades."""

import json

import httpx
import pytest

from valstorm import AsyncValstormClient, PatAuth


@pytest.fixture
def async_client():
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        method = request.method

        if path == "/v1/object/deal" and method == "POST":
            data = json.loads(request.content)
            return httpx.Response(201, json=[{**d, "id": "deal_001"} for d in data])

        if path == "/v1/object/deal/deal_001" and method == "GET":
            return httpx.Response(200, json={"id": "deal_001", "stage": "Prospecting"})

        if path == "/v1/object/deal/deal_missing" and method == "GET":
            return httpx.Response(404, json={"detail": "Deal not found"})

        if path == "/v1/query" and method == "POST":
            return httpx.Response(200, json=[{"id": "deal_001", "amount": 50000}])

        if path == "/v1/vfs/tree" and method == "GET":
            return httpx.Response(200, json=[{"id": "vaul_async", "name": "Async Vault"}])

        if path == "/v1/schema/deal" and method == "GET":
            return httpx.Response(200, json={"api_name": "deal", "title": "Deal"})

        return httpx.Response(404, json={"detail": "Not found"})

    mock_http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    client = AsyncValstormClient(
        base_url="http://testserver/v1",
        auth=PatAuth("vst_pat_secret"),
        http_client=mock_http,
    )
    return client


@pytest.mark.asyncio
async def test_async_records(async_client):
    created = await async_client.records.create("deal", [{"title": "Big Enterprise Deal"}])
    assert len(created) == 1
    assert created[0]["id"] == "deal_001"

    deal = await async_client.records.get("deal", "deal_001")
    assert deal["stage"] == "Prospecting"

    missing = await async_client.records.get("deal", "deal_missing")
    assert missing is None


@pytest.mark.asyncio
async def test_async_query(async_client):
    results = await async_client.query.sql("SELECT * FROM deal")
    assert len(results) == 1
    assert results[0]["amount"] == 50000


@pytest.mark.asyncio
async def test_async_vfs(async_client):
    tree = await async_client.vfs.tree()
    assert len(tree) == 1
    assert tree[0]["name"] == "Async Vault"


@pytest.mark.asyncio
async def test_async_schemas(async_client):
    schema = await async_client.schemas.get("deal")
    assert schema["api_name"] == "deal"
