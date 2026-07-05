"""Home Assistant integration bootstrap for Toya decoder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .api import ToyaDecoderApi
from .const import PLATFORMS
from .coordinator import ToyaDecoderCoordinator
from .data import ToyaDecoderData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    api = ToyaDecoderApi(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
    )
    coordinator = ToyaDecoderCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = ToyaDecoderData(api=api, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the integration and clean up stored data."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
