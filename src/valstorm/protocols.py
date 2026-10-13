"""Structural Protocol definitions ensuring 1:1 parity between PlatformContext and ValstormClient."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class RecordOperations(Protocol):
    """Protocol for record mutations and queries."""

    def create(
        self,
        api_name: str,
        records: dict[str, Any] | list[dict[str, Any]],
    ) -> Any: ...

    def update(
        self,
        api_name: str,
        records: dict[str, Any] | list[dict[str, Any]],
    ) -> Any: ...

    def delete(
        self,
        api_name: str,
        ids: str | list[str],
    ) -> Any: ...

    def get(
        self,
        api_name: str,
        record_id: str,
    ) -> Any: ...

    def list(
        self,
        api_name: str,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "created_date DESC",
        filters: dict[str, Any] | None = None,
    ) -> Any: ...


@runtime_checkable
class QueryOperations(Protocol):
    """Protocol for SQL and GraphQL query execution."""

    def sql(
        self,
        query: str,
        limit: int | None = None,
        hydrate: bool = False,
        bypass_cache: bool = False,
        **kwargs: Any,
    ) -> Any: ...

    def graphql(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> Any: ...


@runtime_checkable
class SchemaOperations(Protocol):
    """Protocol for schema and object definition discovery."""

    def get(self, api_name: str) -> Any: ...

    def list(self) -> Any: ...

    def create(self, schema_data: dict[str, Any]) -> Any: ...

    def update(self, api_name: str, schema_data: dict[str, Any]) -> Any: ...

    def delete(self, api_name: str) -> Any: ...

    def add_field(self, api_name: str, field_data: dict[str, Any]) -> Any: ...

    def delete_field(self, api_name: str, field_name: str) -> Any: ...


@runtime_checkable
class VfsOperations(Protocol):
    """Protocol for Virtual File Service navigation and tree operations."""

    def tree(self) -> Any: ...

    def snapshot(self, bypass_cache: bool = False) -> Any: ...

    def move(
        self,
        item_id: str,
        from_vault_id: str | None = None,
        to_vault_id: str | None = None,
    ) -> Any: ...

    def batch_move(self, items: list[dict[str, Any]]) -> Any: ...

    def get_vault(self, vault_id: str) -> Any: ...

    def resolve_path(self, path: str) -> Any: ...

    def get_file_details(self, file_id: str) -> Any: ...

    def download_file_attachment(self, file_id: str) -> Any: ...

    def delete(self, item_id: str) -> Any: ...

    def batch_delete(self, items: list[str]) -> Any: ...


@runtime_checkable
class FileOperations(Protocol):
    """Protocol for file upload, registration, versioning, and download."""

    def get(self, file_id: str) -> Any: ...

    def register(self, file_data: dict[str, Any]) -> Any: ...

    def save_content(self, file_id: str, content: str) -> Any: ...

    def presigned_upload(
        self,
        filename: str,
        mime_type: str = "application/octet-stream",
        vault_id: str | None = None,
    ) -> Any: ...

    def direct_upload(
        self,
        filename: str,
        content: bytes,
        mime_type: str | None = None,
        vault_id: str | None = None,
    ) -> Any: ...

    def get_versions(self, file_id: str) -> Any: ...

    def rollback(self, file_id: str, version_number: int) -> Any: ...

    def delete(self, file_id: str) -> Any: ...


@runtime_checkable
class AppOperations(Protocol):
    """Protocol for installed applications and marketplace operations."""

    def list_installed(self) -> Any: ...

    def list_marketplace(self) -> Any: ...

    def get(self, app_id: str) -> Any: ...

    def install(self, app_id: str) -> Any: ...

    def bulk_install(self, app_ids: list[str]) -> Any: ...


@runtime_checkable
class SandboxOperations(Protocol):
    """Protocol for isolated organization sandbox environments."""

    def create(self, name: str, source_org_id: str | None = None) -> Any: ...

    def delete(self, sandbox_id: str) -> Any: ...


@runtime_checkable
class PlatformProtocol(Protocol):
    """Master protocol satisfied by both PlatformContext (in-process) and ValstormClient (remote)."""

    records: RecordOperations
    query: QueryOperations
    schemas: SchemaOperations
    vfs: VfsOperations
    files: FileOperations
    apps: AppOperations
    sandboxes: SandboxOperations
