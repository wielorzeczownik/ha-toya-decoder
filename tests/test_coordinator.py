"""Tests for the Toya decoder coordinator."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

from homeassistant.config_entries import SOURCE_REAUTH
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.toya_decoder.api import (
    ToyaDecoderAuthError,
    ToyaDecoderConnectionError,
)
from custom_components.toya_decoder.const import DOMAIN
from custom_components.toya_decoder.coordinator import ToyaDecoderCoordinator

from .conftest import (
    MOCK_CONFIG_ENTRY_DATA,
    MOCK_DEVICE,
    MOCK_USERNAME,
    make_mock_api,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


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


async def test_auth_error_starts_reauth_instead_of_retrying(
    hass: HomeAssistant,
) -> None:
    """Rejected credentials hand the entry to the reauthentication flow."""
    api = make_mock_api()
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ENTRY_DATA,
        unique_id=MOCK_USERNAME,
    )
    entry.add_to_hass(hass)

    with patch(f"custom_components.{DOMAIN}.ToyaDecoderApi", return_value=api):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

        api.async_get_devices.side_effect = ToyaDecoderAuthError(
            "User not authorised"
        )
        await entry.runtime_data.coordinator.async_refresh()
        await hass.async_block_till_done()

    sources = [
        flow["context"]["source"]
        for flow in hass.config_entries.flow.async_progress_by_handler(DOMAIN)
    ]
    assert SOURCE_REAUTH in sources
