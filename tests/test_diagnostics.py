"""Tests for the Toya decoder diagnostics."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.toya_decoder.const import DOMAIN

from .conftest import MOCK_CONFIG_ENTRY_DATA, MOCK_USERNAME, make_mock_api


async def _setup_entry(hass: HomeAssistant):
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
    return entry


async def test_diagnostics_redacts_credentials(hass: HomeAssistant) -> None:
    """Diagnostics output must not contain username or password."""
    from homeassistant.components.diagnostics import async_redact_data

    entry = await _setup_entry(hass)

    from custom_components.toya_decoder.diagnostics import (
        async_get_config_entry_diagnostics,
    )

    result = await async_get_config_entry_diagnostics(hass, entry)
    result_str = str(result)

    assert MOCK_CONFIG_ENTRY_DATA[CONF_USERNAME] not in result_str
    assert MOCK_CONFIG_ENTRY_DATA[CONF_PASSWORD] not in result_str


async def test_diagnostics_contains_coordinator_info(
    hass: HomeAssistant,
) -> None:
    """Diagnostics includes coordinator last_update_success."""
    entry = await _setup_entry(hass)

    from custom_components.toya_decoder.diagnostics import (
        async_get_config_entry_diagnostics,
    )

    result = await async_get_config_entry_diagnostics(hass, entry)

    assert "coordinator" in result
    assert "last_update_success" in result["coordinator"]
    assert "api" in result
