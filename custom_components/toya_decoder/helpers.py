"""Shared helper utilities for the Toya decoder integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.translation import async_get_translations

from .const import DEFAULT_NAME, DOMAIN


async def async_get_default_name(
    hass: HomeAssistant, language: str | None = None
) -> str:
    """Return the localized default name for this integration."""
    translations = await async_get_translations(
        hass,
        language or hass.config.language,
        "common",
        [DOMAIN],
    )
    return translations.get(
        f"component.{DOMAIN}.common.default_name", DEFAULT_NAME
    )
