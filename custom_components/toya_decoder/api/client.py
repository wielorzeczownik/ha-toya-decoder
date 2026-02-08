"""API client for the Toya legacy decoder."""

from __future__ import annotations

import asyncio
import xmlrpc.client
from typing import Any

from ..const import (
    DEFAULT_ENDPOINT,
    DEFAULT_MODEL,
    DEFAULT_VERSION,
    DeviceStatus,
)
from .auth import extract_token, is_auth_fault_message, raise_if_auth_fault
from .channels import extract_products_xml, parse_channels
from .devices import parse_devices
from .errors import (
    ToyaDecoderApiError,
    ToyaDecoderAuthError,
    ToyaDecoderConnectionError,
)
from .models import ToyaDecoderChannel, ToyaDecoderDevice, ToyaDecoderState
from .transport import make_client
from .utils import build_device_id, normalize_cmd


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
        self._device_id = device_id or build_device_id()
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

        cmd = normalize_cmd(key)
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
        token = extract_token(auth_res)

        set_version_res = self._call(
            "toyago.SetVersion",
            [self._device_id, f"{self._version}-{self._model}", token],
        )

        self._token = token
        self._set_version = str(set_version_res)

        return token

    def _call(self, method: str, params: list[Any]) -> Any:
        """Call a raw XML-RPC method and translate failures."""
        client = make_client(self._endpoint, self._timeout_s)
        try:
            res = client.__getattr__(method)(*params)
            raise_if_auth_fault(res)

            return res
        except xmlrpc.client.Fault as err:
            if method == "toyago.GetAuth" or is_auth_fault_message(
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

        return parse_devices(res)

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
                xml = extract_products_xml(res)
                if not xml or xml == "[object Object]":
                    continue

                parsed = parse_channels(xml)
                if parsed:
                    return parsed

        raise ToyaDecoderApiError("No channels parsed from GetProducts")
