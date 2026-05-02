"""Shared fixtures for Toya decoder integration tests."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.toya_decoder.api import (
    ToyaDecoderApi,
    ToyaDecoderChannel,
    ToyaDecoderDevice,
)
from custom_components.toya_decoder.const import DOMAIN, DeviceStatus

MOCK_USERNAME = "test@example.com"
MOCK_PASSWORD = "secret"
MOCK_NAME = "My Decoder"
MOCK_SMART_CARD = "SC123456"
MOCK_CHIP_ID = "CHIP001"

# With _attr_has_entity_name=True, HA builds entity_id from device_name + entity_name.
# Both equal "{MOCK_NAME} {MOCK_SMART_CARD}", so they're concatenated when slugified.
MOCK_ENTITY_ID = "media_player.my_decoder_sc123456_my_decoder_sc123456"

MOCK_CONFIG_ENTRY_DATA = {
    "username": MOCK_USERNAME,
    "password": MOCK_PASSWORD,
    "name": MOCK_NAME,
}

MOCK_DEVICE = ToyaDecoderDevice(
    smart_card=MOCK_SMART_CARD,
    status=DeviceStatus.ON,
    chip_id=MOCK_CHIP_ID,
)

MOCK_CHANNEL = ToyaDecoderChannel(
    id="ch1",
    number=1,
    name="TVP1",
    thumbnail=None,
)


def make_mock_api(
    devices: list[ToyaDecoderDevice] | None = None,
    channels: list[ToyaDecoderChannel] | None = None,
    login_error: Exception | None = None,
) -> MagicMock:
    """Return a mocked ToyaDecoderApi."""
    api = MagicMock(spec=ToyaDecoderApi)
    api._endpoint = "https://api.example.com"
    api._version = "2.3.20"
    api._model = "homeassistant"
    api._device_id = "ha-testdevice"
    api._timeout_s = 10.0
    api._key_delay_s = 0.25

    if login_error:
        api.async_login = AsyncMock(side_effect=login_error)
    else:
        api.async_login = AsyncMock(return_value="mock-token")

    api.async_get_devices = AsyncMock(
        return_value=devices if devices is not None else [MOCK_DEVICE]
    )
    api.async_get_channels = AsyncMock(
        return_value=channels if channels is not None else [MOCK_CHANNEL]
    )
    api.async_send_key = AsyncMock(return_value=None)
    api.async_set_channel = AsyncMock(return_value=None)
    return api


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: HomeAssistant,
) -> None:
    """Enable custom integrations for all tests."""


@pytest.fixture
def mock_api() -> MagicMock:
    """Return a default mock API."""
    return make_mock_api()


@pytest.fixture
def mock_api_patch(mock_api: MagicMock) -> Generator[MagicMock, None, None]:
    """Patch ToyaDecoderApi constructor to return mock_api."""
    with patch(
        f"custom_components.{DOMAIN}.api.ToyaDecoderApi",
        return_value=mock_api,
    ) as patched:
        yield patched
