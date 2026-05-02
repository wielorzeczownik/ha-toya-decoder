"""Tests for the Toya decoder media player entity."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from homeassistant.components.media_player.const import (
    MediaPlayerState,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.toya_decoder.api import ToyaDecoderDevice
from custom_components.toya_decoder.const import DOMAIN, DeviceStatus

from .conftest import (
    MOCK_CHANNEL,
    MOCK_CHIP_ID,
    MOCK_CONFIG_ENTRY_DATA,
    MOCK_DEVICE,
    MOCK_ENTITY_ID,
    MOCK_SMART_CARD,
    MOCK_USERNAME,
    make_mock_api,
)


def _patch_api(api=None):
    if api is None:
        api = make_mock_api()
    return patch(
        f"custom_components.{DOMAIN}.ToyaDecoderApi",
        return_value=api,
    )


async def _setup_entry(hass: HomeAssistant, api=None):
    """Create and load a config entry, return (entry, api)."""
    if api is None:
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
    return entry, api


async def test_entity_state_on(hass: HomeAssistant) -> None:
    """Entity is playing when device status is ON."""
    api = make_mock_api(devices=[MOCK_DEVICE])
    await _setup_entry(hass, api)

    entity_id = MOCK_ENTITY_ID
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == MediaPlayerState.PLAYING


async def test_entity_state_off(hass: HomeAssistant) -> None:
    """Entity is off when device status is OFF."""
    device_off = ToyaDecoderDevice(
        smart_card=MOCK_SMART_CARD,
        status=DeviceStatus.OFF,
        chip_id=MOCK_CHIP_ID,
    )
    api = make_mock_api(devices=[device_off])
    await _setup_entry(hass, api)

    entity_id = MOCK_ENTITY_ID
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == MediaPlayerState.OFF


async def test_play_media_by_channel_number(hass: HomeAssistant) -> None:
    """play_media with a numeric string tunes to that channel."""
    api = make_mock_api()
    entry, api = await _setup_entry(hass, api)

    entity_id = MOCK_ENTITY_ID
    await hass.services.async_call(
        "media_player",
        "play_media",
        {
            "entity_id": entity_id,
            "media_content_type": "channel",
            "media_content_id": "1",
        },
        blocking=True,
    )

    api.async_set_channel.assert_called_once_with(MOCK_SMART_CARD, "1")


async def test_play_media_by_channel_label(hass: HomeAssistant) -> None:
    """play_media with a label tunes to the matching channel number."""
    api = make_mock_api(channels=[MOCK_CHANNEL])
    entry, api = await _setup_entry(hass, api)

    entity_id = MOCK_ENTITY_ID
    await hass.services.async_call(
        "media_player",
        "play_media",
        {
            "entity_id": entity_id,
            "media_content_type": "channel",
            "media_content_id": f"1 {MOCK_CHANNEL.name}",
        },
        blocking=True,
    )

    api.async_set_channel.assert_called_once_with(MOCK_SMART_CARD, "1")


async def test_play_media_unknown_raises(hass: HomeAssistant) -> None:
    """play_media with an unresolvable media_id raises ServiceValidationError."""
    api = make_mock_api(channels=[MOCK_CHANNEL])
    entry, api = await _setup_entry(hass, api)

    entity_id = MOCK_ENTITY_ID
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            "media_player",
            "play_media",
            {
                "entity_id": entity_id,
                "media_content_type": "channel",
                "media_content_id": "nonexistent_channel",
            },
            blocking=True,
        )


async def test_turn_on_is_noop_when_already_on(hass: HomeAssistant) -> None:
    """turn_on is a no-op when the device is already on (power toggle not sent)."""
    api = make_mock_api(devices=[MOCK_DEVICE])
    await _setup_entry(hass, api)

    entity_id = MOCK_ENTITY_ID
    await hass.services.async_call(
        "media_player", "turn_on", {"entity_id": entity_id}, blocking=True
    )

    api.async_send_key.assert_not_called()


async def test_turn_off_sends_power(hass: HomeAssistant) -> None:
    """turn_off sends power command when device is on."""
    api = make_mock_api(devices=[MOCK_DEVICE])
    await _setup_entry(hass, api)

    entity_id = MOCK_ENTITY_ID
    await hass.services.async_call(
        "media_player", "turn_off", {"entity_id": entity_id}, blocking=True
    )

    api.async_send_key.assert_called_once_with(MOCK_SMART_CARD, "power")
