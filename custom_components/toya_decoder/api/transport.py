"""Transport helpers for XML-RPC requests."""

from __future__ import annotations

import ssl
import xmlrpc.client
from typing import Any
from urllib.parse import urlparse


class _TimeoutTransport(xmlrpc.client.Transport):
    """Transport that applies a socket timeout."""

    def __init__(self, timeout_s: float) -> None:
        super().__init__()
        self._timeout_s = timeout_s

    def make_connection(self, host: str) -> Any:
        conn = super().make_connection(host)
        conn.timeout = self._timeout_s

        return conn


class _TimeoutSafeTransport(xmlrpc.client.SafeTransport):
    """TLS transport that applies a socket timeout."""

    def __init__(self, timeout_s: float) -> None:
        super().__init__(context=ssl.create_default_context())
        self._timeout_s = timeout_s

    def make_connection(self, host: str) -> Any:
        conn = super().make_connection(host)
        conn.timeout = self._timeout_s

        return conn


def make_client(endpoint: str, timeout_s: float) -> xmlrpc.client.ServerProxy:
    """Create an XML-RPC client with the requested timeout."""
    parsed = urlparse(endpoint)
    if parsed.scheme == "https":
        transport: xmlrpc.client.Transport = _TimeoutSafeTransport(timeout_s)
    else:
        transport = _TimeoutTransport(timeout_s)

    return xmlrpc.client.ServerProxy(
        endpoint,
        allow_none=True,
        use_builtin_types=True,
        transport=transport,
    )
