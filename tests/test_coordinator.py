"""Tests for the Toya decoder coordinator."""

from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.toya_decoder.api import ToyaDecoderConnectionError
from custom_components.toya_decoder.coordinator import ToyaDecoderCoordinator

from .conftest import MOCK_DEVICE, make_mock_api


async def test_coordinator_fetches_devices(hass: HomeAssistant) -> None:
    """Coordinator returns device list from the API."""
    api = make_mock_api(devices=[MOCK_DEVICE])
    coordinator = ToyaDecoderCoordinator(hass, api)
    await coordinator.async_refresh()

    assert coordinator.data == [MOCK_DEVICE]


async def test_coordinator_marks_failure_on_error(
    hass: HomeAssistant,
) -> None:
    """API errors cause last_update_success to be False."""
    api = make_mock_api()
    coordinator = ToyaDecoderCoordinator(hass, api)
    await coordinator.async_refresh()
    assert coordinator.last_update_success is True

    api.async_get_devices.side_effect = ToyaDecoderConnectionError("timeout")
    await coordinator.async_refresh()
    assert coordinator.last_update_success is False
