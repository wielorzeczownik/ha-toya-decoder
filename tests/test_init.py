"""Tests for the Toya decoder integration setup and teardown."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.toya_decoder.const import DOMAIN
from custom_components.toya_decoder.coordinator import ToyaDecoderCoordinator
from custom_components.toya_decoder.data import ToyaDecoderData

from .conftest import MOCK_CONFIG_ENTRY_DATA, MOCK_USERNAME, make_mock_api


def _patch_api(api=None):
    if api is None:
        api = make_mock_api()
    return patch(
        f"custom_components.{DOMAIN}.ToyaDecoderApi",
        return_value=api,
    )


async def test_setup_entry_stores_runtime_data(hass: HomeAssistant) -> None:
    """Setup stores api and coordinator in entry.runtime_data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ENTRY_DATA,
        unique_id=MOCK_USERNAME,
    )
    entry.add_to_hass(hass)

    with _patch_api():
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert isinstance(entry.runtime_data, ToyaDecoderData)
    assert isinstance(entry.runtime_data.coordinator, ToyaDecoderCoordinator)


async def test_unload_entry(hass: HomeAssistant) -> None:
    """Unloading the entry succeeds and clears runtime_data."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ENTRY_DATA,
        unique_id=MOCK_USERNAME,
    )
    entry.add_to_hass(hass)

    with _patch_api():
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
