"""Diagnostics support for the Toya decoder integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .api.models import ToyaDecoderDevice
from .const import DOMAIN

if TYPE_CHECKING:
    from .api import ToyaDecoderApi
    from .coordinator import ToyaDecoderCoordinator

REDACT_KEYS = {
    CONF_USERNAME,
    CONF_PASSWORD,
    "smart_card",
    "chip_id",
    "token",
}


def _device_to_dict(device: ToyaDecoderDevice) -> dict[str, Any]:
    return {
        "smart_card": device.smart_card,
        "chip_id": device.chip_id,
        "status": device.status.name,
        "status_value": int(device.status),
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    coordinator: ToyaDecoderCoordinator | None = data.get("coordinator")
    api: ToyaDecoderApi | None = data.get("api")

    interval = coordinator.update_interval if coordinator else None

    diagnostics: dict[str, Any] = {
        "entry": {
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success
            if coordinator
            else None,
            "update_interval_seconds": interval.total_seconds()
            if interval
            else None,
            "data": (
                [_device_to_dict(d) for d in (coordinator.data or [])]
                if coordinator
                else []
            ),
        },
        "api": {
            "endpoint": api._endpoint if api else None,
            "version": api._version if api else None,
            "model": api._model if api else None,
            "device_id": api._device_id if api else None,
            "timeout_s": api._timeout_s if api else None,
            "key_delay_s": api._key_delay_s if api else None,
        },
    }

    return async_redact_data(diagnostics, REDACT_KEYS)
