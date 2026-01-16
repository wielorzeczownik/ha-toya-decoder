"""Config flow for the Toya decoder integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .api import (
    ToyaDecoderApi,
    ToyaDecoderAuthError,
    ToyaDecoderConnectionError,
)
from .const import (
    CONF_NAME,
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
)
from .helpers import async_get_default_name


def _unique_id_from_username(username: str) -> str:
    """Normalize the username used as unique id."""

    return username.strip().lower()


async def _validate_input(data: dict, default_name: str) -> dict:
    """Validate user credentials and fetch devices."""
    api = ToyaDecoderApi(
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
    )
    await api.async_login()
    devices = await api.async_get_devices()

    return {
        "title": data.get(CONF_NAME) or default_name,
        "devices": devices,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial configuration flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """Handle the initial step from the UI."""
        errors: dict[str, str] = {}
        default_name = await async_get_default_name(
            self.hass, self.context.get("language")
        )

        if user_input is not None:
            username = user_input[CONF_USERNAME]
            await self.async_set_unique_id(_unique_id_from_username(username))
            self._abort_if_unique_id_configured()

            try:
                info = await _validate_input(user_input, default_name)
            except ToyaDecoderAuthError:
                errors["base"] = "invalid_auth"
            except ToyaDecoderConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                devices = info["devices"]
                if not devices:
                    errors["base"] = "no_devices"
                else:
                    return self.async_create_entry(
                        title=info["title"], data=user_input
                    )

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_NAME, default=default_name): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )
