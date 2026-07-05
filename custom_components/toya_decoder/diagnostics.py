"""Diagnostics support for the Toya decoder integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .api.models import ToyaDecoderDevice
    from .data import ToyaDecoderData

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
    hass: HomeAssistant,  # noqa: ARG001  # signature mandated by the diagnostics platform
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    runtime: ToyaDecoderData = entry.runtime_data
    coordinator = runtime.coordinator
    api = runtime.api

    interval = coordinator.update_interval

    diagnostics: dict[str, Any] = {
        "entry": {
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval_seconds": interval.total_seconds()
            if interval
            else None,
            "data": [_device_to_dict(d) for d in (coordinator.data or [])],
        },
        "api": {
            "endpoint": api.endpoint,
            "version": api.version,
            "model": api.model,
            "device_id": api.device_id,
            "timeout_s": api.timeout_s,
            "key_delay_s": api.key_delay_s,
        },
    }

    return async_redact_data(diagnostics, REDACT_KEYS)
