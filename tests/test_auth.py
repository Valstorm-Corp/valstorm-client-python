"""Tests for authentication strategies and token lifecycle."""

import json

import httpx
import pytest

from valstorm.auth import (
    PatAuth,
    ServiceKeyAuth,
    UserJwtAuth,
    decode_jwt_unverified,
    is_jwt_expiring,
)


def test_pat_auth():
    auth = PatAuth("vst_pat_test123")
    headers = auth.get_auth_headers()
    assert headers == {"Authorization": "Bearer vst_pat_test123"}


@pytest.mark.asyncio
async def test_pat_auth_async():
    auth = PatAuth("vst_pat_test123")
    headers = await auth.get_auth_headers_async()
    assert headers == {"Authorization": "Bearer vst_pat_test123"}


def test_service_key_auth_with_org():
    auth = ServiceKeyAuth("vst_sk_secret", organization_id="org_alpha")
    headers = auth.get_auth_headers()
    assert headers == {
        "Authorization": "Bearer vst_sk_secret",
        "X-Organization-ID": "org_alpha",
    }


def test_service_key_auth_without_org():
    auth = ServiceKeyAuth("vst_sk_secret")
    headers = auth.get_auth_headers()
    assert headers == {"Authorization": "Bearer vst_sk_secret"}


def test_jwt_decode_unverified():
    # Header: {"alg":"HS256","typ":"JWT"} -> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
    # Payload: {"sub":"user_1","exp":1893456000} -> eyJzdWIiOiJ1c2VyXzEiLCJleHAiOjE4OTM0NTYwMDB9
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEiLCJleHAiOjE4OTM0NTYwMDB9.signature"
    claims = decode_jwt_unverified(token)
    assert claims["sub"] == "user_1"
    assert claims["exp"] == 1893456000
    assert not is_jwt_expiring(token)


def test_jwt_expired():
    # Expired token in the past: exp = 1000000000
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEiLCJleHAiOjEwMDAwMDAwMDB9.signature"
    assert is_jwt_expiring(token)


def test_user_jwt_refresh_sync():
    refreshed_tokens = []

    def on_refresh(new_acc, new_ref):
        refreshed_tokens.append((new_acc, new_ref))

    auth = UserJwtAuth(
        access_token="old_access",
        refresh_token="valid_refresh",
        on_refresh=on_refresh,
    )

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/oauth2/refresh":
            data = json.loads(request.content)
            if data.get("refresh_token") == "valid_refresh":
                return httpx.Response(
                    200,
                    json={
                        "access_token": "new_access_token_123",
                        "refresh_token": "new_refresh_token_456",
                    },
                )
        return httpx.Response(400, json={"detail": "Bad Request"})

    mock_client = httpx.Client(transport=httpx.MockTransport(mock_handler))
    success = auth.refresh("http://localhost:8010/v1", http_client=mock_client)

    assert success is True
    assert auth.access_token == "new_access_token_123"
    assert auth.refresh_token == "new_refresh_token_456"
    assert len(refreshed_tokens) == 1
    assert refreshed_tokens[0] == ("new_access_token_123", "new_refresh_token_456")


@pytest.mark.asyncio
async def test_user_jwt_refresh_async():
    refreshed_tokens = []

    async def on_refresh(new_acc, new_ref):
        refreshed_tokens.append((new_acc, new_ref))

    auth = UserJwtAuth(
        access_token="old_access",
        refresh_token="valid_refresh",
        on_refresh=on_refresh,
    )

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/oauth2/refresh":
            return httpx.Response(
                200,
                json={
                    "access_token": "new_async_access",
                    "refresh_token": "new_async_refresh",
                },
            )
        return httpx.Response(400, json={"detail": "Bad Request"})

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(mock_handler))
    success = await auth.refresh_async("http://localhost:8010/v1", http_client=mock_client)

    assert success is True
    assert auth.access_token == "new_async_access"
    assert auth.refresh_token == "new_async_refresh"
    assert len(refreshed_tokens) == 1
    assert refreshed_tokens[0] == ("new_async_access", "new_async_refresh")
