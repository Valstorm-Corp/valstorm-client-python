"""Base classes for synchronous and asynchronous domain facades."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from valstorm.client import AsyncValstormClient, ValstormClient


class SyncBaseFacade:
    """Base class for synchronous domain facades."""

    def __init__(self, client: "ValstormClient"):
        self._client = client
        self._transport = client._transport


class AsyncBaseFacade:
    """Base class for asynchronous domain facades."""

    def __init__(self, client: "AsyncValstormClient"):
        self._client = client
        self._transport = client._transport
