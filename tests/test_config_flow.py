"""Tests for the Toya decoder config flow."""

from __future__ import annotations

from contextlib import ExitStack, contextmanager
from unittest.mock import patch

from homeassistant.config_entries import SOURCE_REAUTH, SOURCE_USER
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.toya_decoder.api import (
    ToyaDecoderAuthError,
    ToyaDecoderConnectionError,
)
from custom_components.toya_decoder.const import DOMAIN

from .conftest import (
    MOCK_CONFIG_ENTRY_DATA,
    MOCK_NAME,
    MOCK_PASSWORD,
    MOCK_USERNAME,
    make_mock_api,
)


@contextmanager
def _patch_api(api=None):
    """Patch ToyaDecoderApi in both config_flow and __init__ (HA auto-sets up entry)."""
    if api is None:
        api = make_mock_api()
    with ExitStack() as stack:
        stack.enter_context(
            patch(
                "custom_components.toya_decoder.config_flow.ToyaDecoderApi",
                return_value=api,
            )
        )
        stack.enter_context(
            patch(
                "custom_components.toya_decoder.ToyaDecoderApi",
                return_value=api,
            )
        )
        yield


async def test_user_step_creates_entry(hass: HomeAssistant) -> None:
    """Happy path: valid credentials create a config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with _patch_api():
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG_ENTRY_DATA,
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == MOCK_NAME
    assert result["data"][CONF_USERNAME] == MOCK_USERNAME
    assert result["data"][CONF_PASSWORD] == MOCK_PASSWORD


async def test_user_step_invalid_auth(hass: HomeAssistant) -> None:
    """Auth error shows the form again with invalid_auth error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    api = make_mock_api(login_error=ToyaDecoderAuthError("bad creds"))
    with _patch_api(api):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG_ENTRY_DATA,
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"


async def test_user_step_cannot_connect(hass: HomeAssistant) -> None:
    """Connection error shows the form again with cannot_connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    api = make_mock_api(login_error=ToyaDecoderConnectionError("timeout"))
    with _patch_api(api):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG_ENTRY_DATA,
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"


async def test_user_step_no_devices(hass: HomeAssistant) -> None:
    """Empty device list shows the form again with no_devices error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    api = make_mock_api(devices=[])
    with _patch_api(api):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG_ENTRY_DATA,
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "no_devices"


async def test_user_step_unknown_error(hass: HomeAssistant) -> None:
    """Unexpected exception shows the form again with unknown error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    api = make_mock_api(login_error=RuntimeError("boom"))
    with _patch_api(api):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG_ENTRY_DATA,
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "unknown"


async def test_user_step_duplicate_aborts(hass: HomeAssistant) -> None:
    """A second flow for the same username is aborted."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ENTRY_DATA,
        unique_id=MOCK_USERNAME,
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    with _patch_api():
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input=MOCK_CONFIG_ENTRY_DATA,
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reauth_success(hass: HomeAssistant) -> None:
    """Reauth with valid password reloads the entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ENTRY_DATA,
        unique_id=MOCK_USERNAME,
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_REAUTH, "entry_id": entry.entry_id},
        data=MOCK_CONFIG_ENTRY_DATA,
    )
    assert result["step_id"] == "reauth_confirm"

    with _patch_api():
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_PASSWORD: "newpassword"},
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"


async def test_reauth_invalid_auth(hass: HomeAssistant) -> None:
    """Reauth with wrong password shows error."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ENTRY_DATA,
        unique_id=MOCK_USERNAME,
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_REAUTH, "entry_id": entry.entry_id},
        data=MOCK_CONFIG_ENTRY_DATA,
    )

    api = make_mock_api(login_error=ToyaDecoderAuthError("bad"))
    with _patch_api(api):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_PASSWORD: "wrongpassword"},
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"


async def test_reconfigure_success(hass: HomeAssistant) -> None:
    """Reconfigure with valid password reloads the entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ENTRY_DATA,
        unique_id=MOCK_USERNAME,
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "reconfigure", "entry_id": entry.entry_id},
    )
    assert result["step_id"] == "reconfigure"

    with _patch_api():
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_PASSWORD: "newpassword", CONF_NAME: MOCK_NAME},
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"


async def test_reconfigure_invalid_auth(hass: HomeAssistant) -> None:
    """Reconfigure with wrong password shows error."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_ENTRY_DATA,
        unique_id=MOCK_USERNAME,
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "reconfigure", "entry_id": entry.entry_id},
    )

    api = make_mock_api(login_error=ToyaDecoderAuthError("bad"))
    with _patch_api(api):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            user_input={CONF_PASSWORD: "wrongpassword", CONF_NAME: MOCK_NAME},
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_auth"
