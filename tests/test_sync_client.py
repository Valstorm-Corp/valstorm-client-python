"""Tests for synchronous ValstormClient and domain facades."""

import json

import httpx
import pytest

from valstorm import PatAuth, ValstormClient
from valstorm.protocols import (
    AppOperations,
    FileOperations,
    QueryOperations,
    RecordOperations,
    SandboxOperations,
    SchemaOperations,
    VfsOperations,
)


@pytest.fixture
def sync_client():
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        method = request.method

        # Verify standard headers
        assert "Authorization" in request.headers
        assert "X-Request-ID" in request.headers

        # Records endpoints
        if path == "/v1/object/lead" and method == "POST":
            data = json.loads(request.content)
            return httpx.Response(201, json=[{**d, "id": "lead_999"} for d in data])

        if path == "/v1/object/lead" and method == "PATCH":
            data = json.loads(request.content)
            return httpx.Response(200, json=[{**d, "updated": True} for d in data])

        if path == "/v1/object/lead/lead_123" and method == "GET":
            return httpx.Response(200, json={"id": "lead_123", "name": "Alice"})

        if path == "/v1/object/lead/lead_not_found" and method == "GET":
            return httpx.Response(404, json={"detail": "Record not found"})

        if path == "/v1/object/lead/lead_123" and method == "DELETE":
            return httpx.Response(204)

        if path == "/v1/object/lead" and method == "DELETE":
            return httpx.Response(204)

        if path == "/v1/object/lead" and method == "GET":
            return httpx.Response(
                200,
                headers={"X-Total-Count": "42"},
                json=[{"id": "lead_1"}, {"id": "lead_2"}],
            )

        # Query endpoints
        if path == "/v1/query" and method == "POST":
            data = json.loads(request.content)
            assert "query" in data
            return httpx.Response(200, json=[{"id": "lead_1", "status": "Active"}])

        if path == "/v1/graphql" and method == "POST":
            return httpx.Response(200, json={"data": {"lead": {"id": "lead_1"}}})

        # VFS endpoints
        if path == "/v1/vfs/tree" and method == "GET":
            return httpx.Response(200, json=[{"id": "vaul_root", "name": "Root Vault"}])

        if path == "/v1/vfs/snapshot" and method == "GET":
            return httpx.Response(200, json={"vaults": [], "files": []})

        if path == "/v1/vfs/move" and method == "POST":
            return httpx.Response(200, json={"status": "moved"})

        # Schemas endpoints
        if path == "/v1/schema" and method == "GET":
            return httpx.Response(200, json={"lead": {"properties": {}}})

        if path == "/v1/schema/lead" and method == "GET":
            return httpx.Response(200, json={"api_name": "lead", "title": "Lead"})

        # Files endpoints
        if path == "/v1/files/register" and method == "POST":
            return httpx.Response(201, json={"file_id": "file_abc", "status": "registered"})

        # Apps endpoints
        if path == "/v1/apps" and method == "GET":
            return httpx.Response(200, json=[{"id": "app_crm", "name": "CRM"}])

        # Sandboxes endpoints
        if path == "/v1/sandboxes" and method == "POST":
            return httpx.Response(201, json={"sandbox_id": "sbx_test", "status": "ready"})

        return httpx.Response(404, json={"detail": f"Route not matched: {method} {path}"})

    mock_http = httpx.Client(transport=httpx.MockTransport(handler))
    client = ValstormClient(
        base_url="http://testserver/v1",
        auth=PatAuth("vst_pat_secret"),
        http_client=mock_http,
    )
    return client


def test_protocol_conformance(sync_client):
    assert isinstance(sync_client.records, RecordOperations)
    assert isinstance(sync_client.query, QueryOperations)
    assert isinstance(sync_client.vfs, VfsOperations)
    assert isinstance(sync_client.schemas, SchemaOperations)
    assert isinstance(sync_client.files, FileOperations)
    assert isinstance(sync_client.apps, AppOperations)
    assert isinstance(sync_client.sandboxes, SandboxOperations)


def test_sync_records_crud(sync_client):
    # 1. Create
    created = sync_client.records.create("lead", [{"name": "Test Lead"}])
    assert len(created) == 1
    assert created[0]["id"] == "lead_999"

    # 2. Update
    updated = sync_client.records.update("lead", [{"id": "lead_999", "name": "New Name"}])
    assert updated[0]["updated"] is True

    # 3. Get existing
    record = sync_client.records.get("lead", "lead_123")
    assert record["id"] == "lead_123"

    # 4. Get non-existent (should return None, mirroring PlatformContext)
    missing = sync_client.records.get("lead", "lead_not_found")
    assert missing is None

    # 5. List with pagination
    records, total = sync_client.records.list("lead", limit=10, offset=0)
    assert len(records) == 2
    assert total == 42

    # 6. Delete single & batch
    assert sync_client.records.delete("lead", "lead_123") == 1
    assert sync_client.records.delete("lead", ["lead_1", "lead_2"]) == 2


def test_sync_query(sync_client):
    results = sync_client.query.sql("SELECT * FROM lead")
    assert len(results) == 1
    assert results[0]["id"] == "lead_1"

    gql = sync_client.query.graphql("query { lead { id } }")
    assert "data" in gql


def test_sync_vfs(sync_client):
    tree = sync_client.vfs.tree()
    assert len(tree) == 1
    assert tree[0]["id"] == "vaul_root"

    snapshot = sync_client.vfs.snapshot()
    assert "vaults" in snapshot

    moved = sync_client.vfs.move("file_1", to_vault_id="vaul_2")
    assert moved["status"] == "moved"


def test_sync_schemas_files_apps_sandboxes(sync_client):
    schemas = sync_client.schemas.list()
    assert "lead" in schemas

    reg = sync_client.files.register({"filename": "test.txt", "location": "s3://bucket/test.txt"})
    assert reg["file_id"] == "file_abc"

    apps = sync_client.apps.list_installed()
    assert len(apps) == 1

    sbx = sync_client.sandboxes.create(name="test_sandbox")
    assert sbx["sandbox_id"] == "sbx_test"
