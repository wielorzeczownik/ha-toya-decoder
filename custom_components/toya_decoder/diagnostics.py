"""Diagnostics support for the Toya decoder integration."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_PASSWORD, CONF_USERNAME, DOMAIN

REDACT_KEYS = {
    CONF_USERNAME,
    CONF_PASSWORD,
    "smart_card",
    "chip_id",
    "token",
}


def _serialize_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None

    return value.isoformat()


def _device_to_dict(device: Any) -> dict[str, Any]:
    return {
        "smart_card": getattr(device, "smart_card", None),
        "chip_id": getattr(device, "chip_id", None),
        "status": getattr(device, "status", None).name
        if getattr(device, "status", None) is not None
        else None,
        "status_value": int(getattr(device, "status", 0))
        if getattr(device, "status", None) is not None
        else None,
    }


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    coordinator = data.get("coordinator")
    api = data.get("api")

    diagnostics: dict[str, Any] = {
        "entry": {
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "coordinator": {
            "last_update_success": getattr(
                coordinator, "last_update_success", None
            ),
            "last_update_success_time": _serialize_datetime(
                getattr(coordinator, "last_update_success_time", None)
            ),
            "update_interval_seconds": getattr(
                getattr(coordinator, "update_interval", None),
                "total_seconds",
                lambda: None,
            )(),
            "data": [
                _device_to_dict(device)
                for device in (getattr(coordinator, "data", None) or [])
            ],
        },
        "api": {
            "endpoint": getattr(api, "_endpoint", None),
            "version": getattr(api, "_version", None),
            "model": getattr(api, "_model", None),
            "device_id": getattr(api, "_device_id", None),
            "timeout_s": getattr(api, "_timeout_s", None),
            "key_delay_s": getattr(api, "_key_delay_s", None),
        },
    }

    return async_redact_data(diagnostics, REDACT_KEYS)
