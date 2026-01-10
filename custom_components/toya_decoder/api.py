"""API client for the Toya legacy decoder."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import hashlib
import html
import json
import os
import re
import socket
import ssl
from typing import Any
from urllib.parse import urlparse
import xmlrpc.client

from .const import (
    DEFAULT_ENDPOINT,
    DEFAULT_MODEL,
    DEFAULT_VERSION,
    DeviceStatus,
    REMOTE_COMMANDS,
)


@dataclass
class ToyaDecoderState:
    """Represents the overall power state of the decoder."""

    is_on: bool = False


@dataclass
class ToyaDecoderDevice:
    """Represents a decoder device entry from the API."""

    smart_card: str
    status: DeviceStatus
    chip_id: str


@dataclass
class ToyaDecoderChannel:
    """Represents a broadcast channel entry from the API."""

    id: str
    number: int | None
    name: str | None
    thumbnail: str | None


class ToyaDecoderApi:
    """Async wrapper for the decoder XML-RPC protocol."""

    def __init__(
        self,
        username: str,
        password: str,
        endpoint: str = DEFAULT_ENDPOINT,
        version: str = DEFAULT_VERSION,
        model: str = DEFAULT_MODEL,
        device_id: str | None = None,
        key_delay_s: float = 0.25,
        timeout_s: float = 10.0,
    ) -> None:
        self._username = username
        self._password = password
        self._endpoint = endpoint
        self._version = version
        self._model = model
        self._device_id = device_id or _build_device_id()
        self._key_delay_s = key_delay_s
        self._timeout_s = timeout_s
        self._token: str | None = None
        self._set_version: str | None = None

    async def async_get_state(self) -> ToyaDecoderState:
        """Return a simplified power state computed from device status."""
        devices = await self.async_get_devices()
        is_on = any(device.status == DeviceStatus.ON for device in devices)

        return ToyaDecoderState(is_on=is_on)

    async def async_send_key(self, smart_card: str, key: str) -> None:
        """Send a remote control command to a specific smart card."""
        smart_card = str(smart_card).strip()
        if not smart_card:
            raise ToyaDecoderApiError("Missing smart_card")

        cmd = _normalize_cmd(key)
        token = await self.async_login()
        try:
            await asyncio.to_thread(self._send_key, token, smart_card, cmd)
        except ToyaDecoderAuthError:
            self._token = None
            token = await self.async_login()
            await asyncio.to_thread(self._send_key, token, smart_card, cmd)

    async def async_set_channel(self, smart_card: str, channel: str) -> None:
        """Send the channel number as a sequence of digit key presses."""
        digits = str(channel).strip()
        if not digits.isdigit():
            raise ToyaDecoderApiError(f"Invalid channel: {channel}")

        for digit in digits:
            await self.async_send_key(smart_card, digit)
            if self._key_delay_s > 0:
                await asyncio.sleep(self._key_delay_s)

    async def async_login(self) -> str:
        if self._token:
            return self._token

        return await asyncio.to_thread(self._login)

    async def async_get_devices(self) -> list[ToyaDecoderDevice]:
        token = await self.async_login()
        try:
            return await asyncio.to_thread(self._get_pvr_devices, token)
        except ToyaDecoderAuthError:
            self._token = None
            token = await self.async_login()

            return await asyncio.to_thread(self._get_pvr_devices, token)

    async def async_get_channels(self) -> list[ToyaDecoderChannel]:
        token = await self.async_login()
        try:
            return await asyncio.to_thread(self._get_channels, token)
        except ToyaDecoderAuthError:
            self._token = None
            token = await self.async_login()

            return await asyncio.to_thread(self._get_channels, token)

    def _login(self) -> str:
        """Authenticate and cache the token for subsequent calls."""
        if not self._username or not self._password:
            raise ToyaDecoderAuthError("Missing credentials")

        auth_res = self._call(
            "toyago.GetAuth", [self._device_id, self._username, self._password]
        )
        token = _extract_token(auth_res)

        set_version_res = self._call(
            "toyago.SetVersion",
            [self._device_id, f"{self._version}-{self._model}", token],
        )

        self._token = token
        self._set_version = str(set_version_res)

        return token

    def _call(self, method: str, params: list[Any]) -> Any:
        """Call a raw XML-RPC method and translate failures."""
        client = _make_client(self._endpoint, self._timeout_s)
        try:
            res = client.__getattr__(method)(*params)
            _raise_if_auth_fault(res)

            return res
        except xmlrpc.client.Fault as err:
            if method == "toyago.GetAuth" or _is_auth_fault_message(
                err.faultString
            ):
                raise ToyaDecoderAuthError(
                    f"XML-RPC auth fault: {err}"
                ) from err
            raise ToyaDecoderApiError(f"XML-RPC fault: {err}") from err
        except xmlrpc.client.ProtocolError as err:
            raise ToyaDecoderConnectionError(
                f"XML-RPC protocol error: {err}"
            ) from err
        except OSError as err:
            raise ToyaDecoderConnectionError(str(err)) from err

    def _get_pvr_devices(self, token: str) -> list[ToyaDecoderDevice]:
        """Fetch devices for the given auth token."""
        res = self._call("toyago.GetPvrDevices", [self._device_id, token])

        return _parse_devices(res)

    def _send_key(self, token: str, smart_card: str, cmd: str) -> None:
        """Send a command to the decoder using an auth token."""
        self._call(
            "toyago.SetStbCmd", [self._device_id, smart_card, cmd, token]
        )

    def _get_channels(self, token: str) -> list[ToyaDecoderChannel]:
        """Fetch channel list by trying several API variants."""
        product_types = ("channel_dvb", "channel")
        variants: list[tuple[int, int, bool]] = [
            (-1, -1, True),
            (-1, -1, False),
            (0, 1, False),
        ]
        for product_type in product_types:
            for start, end, include in variants:
                res = self._call(
                    "toyago.GetProducts",
                    [
                        self._device_id,
                        product_type,
                        [],
                        start,
                        end,
                        ["0"],
                        include,
                        token,
                    ],
                )
                xml = _extract_products_xml(res)
                if not xml or xml == "[object Object]":
                    continue

                parsed = _parse_channels(xml)
                if parsed:
                    return parsed

        raise ToyaDecoderApiError("No channels parsed from GetProducts")


def _extract_products_xml(res: Any) -> str:
    """Normalize GetProducts responses into a string XML payload."""
    if res is None:
        return ""

    if isinstance(res, bytes):
        return res.decode(errors="ignore")

    if isinstance(res, str):
        return res

    if isinstance(res, list):
        return "".join(str(item) for item in res)

    if isinstance(res, dict):
        if "products" in res:
            return _extract_products_xml(res["products"])

    return str(res)


def _extract_attr_value(body: str, key: str) -> str | None:
    """Extract a product attribute value from the XML payload."""
    pattern = re.compile(
        rf'<attr\b[^>]*key="{re.escape(key)}"[^>]*>[\s\S]*?<value>([\s\S]*?)</value>',
        re.IGNORECASE,
    )
    match = pattern.search(body)
    if not match:
        return None

    return html.unescape(match.group(1).strip())


def _parse_channels(xml: str) -> list[ToyaDecoderChannel]:
    """Parse channel entries from the GetProducts XML body."""
    out: list[ToyaDecoderChannel] = []
    pattern = re.compile(
        r'<object\b[^>]*type="product"[^>]*id="([^"]+)"[^>]*>([\s\S]*?)</object>',
        re.IGNORECASE,
    )
    for match in pattern.finditer(xml):
        channel_id = match.group(1)
        body = match.group(2)
        name = _extract_attr_value(body, "name") or _extract_attr_value(
            body, "shortTitle"
        )
        thumbnail = _extract_attr_value(body, "thumbnail")
        number_raw = (
            _extract_attr_value(body, "number")
            or _extract_attr_value(body, "channel_number")
            or _extract_attr_value(body, "lcn")
            or _extract_attr_value(body, "position")
        )
        number: int | None = None
        if number_raw:
            try:
                number = int(str(number_raw).strip())
            except ValueError:
                number = None

        out.append(
            ToyaDecoderChannel(
                id=channel_id,
                name=name,
                number=number,
                thumbnail=thumbnail,
            )
        )

    return out


class ToyaDecoderApiError(Exception):
    """General API error."""


class ToyaDecoderConnectionError(ToyaDecoderApiError):
    """Connection or transport error."""


class ToyaDecoderAuthError(ToyaDecoderApiError):
    """Authentication failed."""


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


def _make_client(endpoint: str, timeout_s: float) -> xmlrpc.client.ServerProxy:
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


def _build_device_id() -> str:
    """Build a deterministic device id for the API session."""
    base = f"{socket.gethostname()}|{os.getcwd()}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]

    return f"ha-{digest}"


def _format_response(res: Any) -> str:
    """Format a response for diagnostic messages."""
    try:
        return json.dumps(res)
    except TypeError:
        return repr(res)


def _normalize_token(raw: str) -> str:
    """Normalize token strings returned by XML-RPC responses."""
    token = raw.strip()
    if not token:
        return token

    parts = token.split("=")
    if len(parts) >= 2:
        token = "=".join(parts[1:]).strip()

    if token.endswith(";"):
        token = token[:-1].strip()

    if token.startswith('"') and token.endswith('"') and len(token) >= 2:
        token = token[1:-1]

    return token


def _extract_token_from_value(res: Any) -> str | None:
    """Search nested response structures for a token-like value."""
    if res is None:
        return None

    if isinstance(res, (str, int, bool)):
        token = _normalize_token(str(res))

        return token or None

    if isinstance(res, (list, tuple)):
        for item in res:
            token = _extract_token_from_value(item)
            if token:
                return token

        return None

    if isinstance(res, dict):
        for key in (
            "token",
            "auth",
            "authToken",
            "authorization",
            "result",
            "value",
        ):
            if key in res:
                token = _extract_token_from_value(res[key])
                if token:
                    return token

        values = list(res.values())
        if len(values) == 1:
            return _extract_token_from_value(values[0])

    return None


def _extract_token(res: Any) -> str:
    """Extract a token from a GetAuth response or raise on failure."""
    token = _extract_token_from_value(res)
    if not token:
        raise ToyaDecoderAuthError(
            f"Unexpected GetAuth response: {_format_response(res)}"
        )

    return token


def _normalize_cmd(key: str) -> str:
    """Normalize and validate command names."""
    text = str(key).strip()
    if len(text) == 1 and text.isdigit():
        return text

    cmd = text.lower()
    if cmd in REMOTE_COMMANDS:
        return cmd

    raise ToyaDecoderApiError(f"Unsupported command: {key}")


def _extract_fault_payload(res: Any) -> tuple[str | int | None, str | None]:
    """Extract fault code and message from XML-RPC responses."""
    if isinstance(res, dict):
        code = (
            res.get("faultCode")
            or res.get("faultcode")
            or res.get("fault_code")
        )
        text = (
            res.get("faultString")
            or res.get("faultstring")
            or res.get("fault_string")
            or res.get("message")
        )

        return code, str(text) if text is not None else None

    if isinstance(res, (list, tuple)):
        for item in res:
            code, text = _extract_fault_payload(item)
            if code is not None or text:
                return code, text

    return None, None


def _is_auth_fault_message(text: str | None) -> bool:
    """Return True for fault messages that indicate auth failure."""
    if not text:
        return False

    lowered = text.lower()

    return "not author" in lowered or "unauthor" in lowered


def _is_auth_fault(res: Any) -> bool:
    """Return True when the response encodes an auth failure."""
    code, text = _extract_fault_payload(res)
    if code is None and not text:
        return False

    if _is_auth_fault_message(text):
        return True

    return str(code) == "2"


def _raise_if_auth_fault(res: Any) -> None:
    """Raise an auth error if the response contains an auth fault."""
    if _is_auth_fault(res):
        raise ToyaDecoderAuthError(
            f"User not authorised: {_format_response(res)}"
        )


def _parse_devices(res: Any) -> list[ToyaDecoderDevice]:
    """Parse device entries from GetPvrDevices responses."""
    if not res:
        return []

    devices: Any = res
    if isinstance(res, dict) and "devices" in res:
        devices = res["devices"]

    if isinstance(devices, (list, tuple)):
        out: list[ToyaDecoderDevice] = []
        for item in devices:
            if not isinstance(item, dict):
                continue

            smart_card = item.get("smartcard")
            chip_id = item.get("chipid")
            status = item.get("status", 0)
            if smart_card and chip_id is not None:
                out.append(
                    ToyaDecoderDevice(
                        str(smart_card),
                        _status_from_value(status),
                        str(chip_id),
                    )
                )

        return out

    raw = str(devices)
    raw = raw.strip()
    if (raw.startswith("[") and raw.endswith("]")) or (
        raw.startswith("{") and raw.endswith("}")
    ):
        raw = raw[1:-1]

    parts = [part for part in re.split(r"=|, |\}\{|\{|\}", raw) if part]
    out = []
    key = ""
    smart_card: str | None = None
    chip_id: str | None = None
    status: DeviceStatus | None = None

    for idx, part in enumerate(parts):
        if idx % 2 == 0:
            key = part
            continue

        value = part
        if key == "status":
            status = _status_from_value(value)
        elif key == "smartcard":
            smart_card = value
        elif key == "chipid":
            chip_id = value

        if (
            smart_card is not None
            and status is not None
            and chip_id is not None
        ):
            out.append(ToyaDecoderDevice(smart_card, status, chip_id=chip_id))
            smart_card = None
            chip_id = None
            status = None

    return out


def _safe_int(value: Any) -> int:
    """Convert to int or return 0."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _status_from_value(value: Any) -> DeviceStatus:
    """Convert status values to DeviceStatus enum."""
    numeric = _safe_int(value)
    try:
        return DeviceStatus(numeric)
    except ValueError:
        return DeviceStatus.UNKNOWN
