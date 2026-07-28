"""Home Assistant integration bootstrap for Toya decoder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er

from .api import ToyaDecoderApi
from .const import DOMAIN
from .coordinator import ToyaDecoderCoordinator
from .data import ToyaDecoderData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

PLATFORMS = [Platform.MEDIA_PLAYER]


async def _async_migrate_unique_ids(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Drop the config entry id from entity unique ids."""
    registry = er.async_get(hass)
    prefix = f"{DOMAIN}_{entry.entry_id}_"

    @callback
    def _migrate(entity: er.RegistryEntry) -> dict[str, str] | None:
        if not entity.unique_id.startswith(prefix):
            return None

        new_unique_id = f"{DOMAIN}_{entity.unique_id.removeprefix(prefix)}"
        if registry.async_get_entity_id(entity.domain, DOMAIN, new_unique_id):
            return None
        return {"new_unique_id": new_unique_id}

    await er.async_migrate_entries(hass, entry.entry_id, _migrate)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration from a config entry."""
    await _async_migrate_unique_ids(hass, entry)

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
