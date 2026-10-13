# Valstorm Python Client SDK (`valstorm-client`)

The official Python client library for the **Open Valstorm** platform. Built with Python 3.13+, `httpx`, and `pydantic`.

Provides **1:1 structural interface parity** with the server-side in-process `PlatformContext` (`client.records.*`, `client.query.*`, `client.vfs.*`, `client.schemas.*`, `client.files.*`, `client.apps.*`, `client.sandboxes.*`), enabling unified developer ergonomics across both in-process and remote satellite applications.

---

## Features

- **Dual Sync & Async Transports**:
  - `ValstormClient` — Synchronous, backed by `httpx.Client(http2=True)`. Designed for CLI tools, Celery worker tasks, offline data migrations, and linear Python scripts.
  - `AsyncValstormClient` — Fully asynchronous, backed by `httpx.AsyncClient(http2=True)`. Designed for high-concurrency AI agent loops (`apps/agent-runtime`), FastMCP servers (`apps/valstorm-mcp-server`), and FastAPI applications.
- **1:1 `PlatformContext` Parity**:
  - Shared method names, signatures, and mental models as `apps/open-api/app/core/platform_context.py`.
  - Type-checked via Python `typing.Protocol` interfaces (`PlatformProtocol`).
- **Robust Authentication Strategies**:
  - `PatAuth` — Long-lived Personal Access Tokens (`vst_pat_...`).
  - `ServiceKeyAuth` — Machine-to-Machine keys (`vst_sk_...`) with organization scoping.
  - `UserJwtAuth` — Interactive user OAuth2 tokens with automatic JWT expiration detection and mutexed proactive/reactive refresh.
- **Enterprise Resilience**:
  - HTTP/2 multiplexing and connection pooling.
  - Automatic `X-Request-ID` tracing on every call.
  - Granular exception hierarchy mapping HTTP status codes (`AuthenticationError`, `NotFoundError`, `ValidationError`, `RateLimitError`).

---

## Installation

Using `uv` (recommended):
```bash
uv add valstorm-client
```

Using `pip`:
```bash
pip install valstorm-client
```

---

## Quickstart

### 1. Synchronous Usage (`ValstormClient`)

Ideal for CLI commands, Celery tasks, and ETL scripts:

```python
from valstorm import ValstormClient, PatAuth

client = ValstormClient(
    base_url="http://localhost:8010/v1",
    auth=PatAuth("vst_pat_your_token_here"),
)

# 1. Query data using SQL
leads = client.query.sql("SELECT id, name, status, loan_amount FROM lead WHERE status = 'Active'")
print(f"Found {len(leads)} active leads")

# 2. Create records
new_leads = client.records.create(
    "lead", [{"name": "Alice Morgan", "email": "alice@example.com", "loan_amount": 750000}]
)
print(f"Created lead: {new_leads[0]['id']}")

# 3. List records with pagination
records, total_count = client.records.list("lead", limit=20, offset=0)

# 4. Explore Virtual File Service
vfs_tree = client.vfs.tree()
```

### 2. Asynchronous Usage (`AsyncValstormClient`)

Ideal for AI Agent Runtimes, FastMCP servers, and streaming endpoints:

```python
import asyncio
from valstorm import AsyncValstormClient, UserJwtAuth


async def main():
    async with AsyncValstormClient(
        base_url="http://localhost:8010/v1",
        auth=UserJwtAuth(
            access_token="eyJhbGciOi...",
            refresh_token="ref_12345...",
            on_refresh=lambda new_acc, new_ref: print("Tokens auto-refreshed!"),
        ),
    ) as client:
        # SQL query
        results = await client.query.sql("SELECT * FROM contact LIMIT 5")

        # Virtual File Service snapshot
        snapshot = await client.vfs.snapshot()

        # Schema metadata inspection
        schema = await client.schemas.get("contact")
        print(f"Contact fields: {list(schema.get('properties', {}).keys())}")


asyncio.run(main())
```

---

## Authentication Strategies

### 1. Personal Access Token (PAT)
```python
from valstorm import ValstormClient, PatAuth

client = ValstormClient(auth=PatAuth("vst_pat_abc123"))
```

### 2. Machine-to-Machine Service Key (M2M)
```python
from valstorm import ValstormClient, ServiceKeyAuth

client = ValstormClient(
    auth=ServiceKeyAuth(service_key="vst_sk_xyz789", organization_id="org_marketing_prod")
)
```

### 3. User JWT with Transparent Auto-Refresh
```python
from valstorm import AsyncValstormClient, UserJwtAuth


def save_tokens(access_token: str, refresh_token: str | None):
    # Persist updated tokens to secure store (~/.valstorm/profiles/default.json)
    ...


auth = UserJwtAuth(
    access_token="...",
    refresh_token="...",
    on_refresh=save_tokens,
)
client = AsyncValstormClient(auth=auth)
```

---

## Domain Facades Overview

Both `ValstormClient` and `AsyncValstormClient` expose identical facades:

| Facade | Methods | Description |
|---|---|---|
| `client.records` | `create()`, `update()`, `delete()`, `get()`, `list()` | Record mutations (CUD) and ID lookups |
| `client.query` | `sql()`, `graphql()` | Sanitized SQL execution and dynamic GraphQL |
| `client.schemas` | `get()`, `list()`, `create()`, `update()`, `delete()`, `add_field()`, `delete_field()` | Object definition and DDL schema compiler |
| `client.vfs` | `tree()`, `snapshot()`, `move()`, `batch_move()`, `get_vault()`, `resolve_path()`, `delete()` | Virtual File Service hierarchical vault operations |
| `client.files` | `get()`, `register()`, `save_content()`, `presigned_upload()`, `direct_upload()`, `rollback()` | Binary file storage, attachments, and versioning |
| `client.apps` | `list_installed()`, `list_marketplace()`, `get()`, `install()`, `bulk_install()`, `deploy()` | Marketplace app bundles and fleet tenant deployments |
| `client.sandboxes` | `create()`, `delete()` | Dedicated tenant PostgreSQL database sandboxes |

---

## Error Handling

All HTTP errors are mapped to typed Python exceptions inheriting from `ValstormError`:

```python
from valstorm import ValstormClient
from valstorm.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
)

client = ValstormClient.from_env()

try:
    lead = client.records.get("lead", "non_existent_id")
except NotFoundError:
    print("Record not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds.")
except ValidationError as e:
    print(f"Validation failure: {e.details}")
except AuthenticationError:
    print("Session expired or invalid token")
```

---

## License

This software is distributed under a **Dual License** model:
- **Noncommercial Use**: Governed by the **PolyForm Noncommercial License 1.0.0**.
- **Commercial & Enterprise Use**: Governed by the **Valstorm Commercial License Agreement**.

See `LICENSE.md` and `CONTRIBUTING.md` for full details.
