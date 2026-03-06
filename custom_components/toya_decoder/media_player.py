"""Media player entity for Toya decoder devices."""

from __future__ import annotations

import logging

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
)
from homeassistant.components.media_player.browse_media import BrowseMedia
from homeassistant.components.media_player.const import (
    MediaClass,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.translation import async_get_translations
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import ToyaDecoderChannel, ToyaDecoderDevice
from .const import DOMAIN, REMOTE_COMMANDS, DeviceStatus, RemoteCommand
from .coordinator import ToyaDecoderCoordinator
from .helpers import async_get_default_name

_LOGGER = logging.getLogger(__name__)

_POWER_FEATURES = (
    MediaPlayerEntityFeature.TURN_ON | MediaPlayerEntityFeature.TURN_OFF
)
_SUPPORTED_FEATURES = (
    _POWER_FEATURES
    | MediaPlayerEntityFeature.VOLUME_STEP
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.NEXT_TRACK
    | MediaPlayerEntityFeature.PREVIOUS_TRACK
    | MediaPlayerEntityFeature.PLAY
    | MediaPlayerEntityFeature.PAUSE
    | MediaPlayerEntityFeature.BROWSE_MEDIA
    | MediaPlayerEntityFeature.PLAY_MEDIA
)


def _build_channel_sources(
    channels: list[ToyaDecoderChannel],
) -> dict[str, ToyaDecoderChannel]:
    """Build a label-to-channel mapping for media browsing."""
    sources: dict[str, ToyaDecoderChannel] = {}
    ordered = sorted(
        (channel for channel in channels if channel.number is not None),
        key=lambda channel: channel.number or 0,
    )
    for channel in ordered:
        number = str(channel.number)
        label = f"{number} {channel.name}" if channel.name else number
        sources[label] = channel

    return sources


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up media player entities for the config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ToyaDecoderCoordinator = data["coordinator"]

    default_name = await async_get_default_name(hass)
    base_name = entry.data.get(CONF_NAME) or default_name
    devices = coordinator.data or []
    if not devices:
        try:
            devices = await coordinator.api.async_get_devices()
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("Failed to fetch devices during setup: %s", err)
            devices = []

    try:
        fetched = await coordinator.api.async_get_channels()
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Failed to fetch channels: %s", err)
        fetched = []
    channels = _build_channel_sources(fetched)
    entities = [
        ToyaLegacyDecoderMediaPlayer(
            base_name, device, coordinator, entry.entry_id, channels
        )
        for device in devices
    ]
    async_add_entities(entities)


class ToyaLegacyDecoderMediaPlayer(
    CoordinatorEntity[ToyaDecoderCoordinator], MediaPlayerEntity
):
    """Media player entity representing a Toya legacy decoder."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:television"
    _attr_device_class = MediaPlayerDeviceClass.TV
    _attr_supported_features = _SUPPORTED_FEATURES

    def __init__(
        self,
        base_name: str,
        device: ToyaDecoderDevice,
        coordinator: ToyaDecoderCoordinator,
        entry_id: str,
        channels: dict[str, ToyaDecoderChannel],
    ) -> None:
        super().__init__(coordinator)
        self._smart_card = device.smart_card
        self._chip_id = device.chip_id
        self._attr_name = f"{base_name} {self._smart_card}"
        self._attr_unique_id = f"toya_decoder_{entry_id}_{self._smart_card}"
        self._channels = channels
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._chip_id)},
            name=f"{base_name} {self._smart_card}",
            manufacturer="Toya",
            model=self._chip_id,
        )
        self._attr_media_content_type = MediaType.CHANNEL
        self._attr_extra_state_attributes = {
            "smart_card": self._smart_card,
            "chip_id": self._chip_id,
            "remote_commands": REMOTE_COMMANDS,
        }
        self._update_supported_features()
        self._update_state()

    def _update_supported_features(self) -> None:
        """Update supported features based on device status."""
        features = _SUPPORTED_FEATURES
        device = self._device()
        if device is None or device.status != DeviceStatus.ON:
            features &= ~_POWER_FEATURES
        self._attr_supported_features = features

    def _update_state(self) -> None:
        """Update state based on device status."""
        device = self._device()
        if device is None:
            self._attr_state = MediaPlayerState.OFF
            return

        self._attr_state = (
            MediaPlayerState.PLAYING
            if device.status == DeviceStatus.ON
            else MediaPlayerState.OFF
        )

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_supported_features()
        self._update_state()
        super()._handle_coordinator_update()

    @property
    def available(self) -> bool:  # type: ignore[override]
        """Return True when the coordinator last updated successfully."""
        return self.coordinator.last_update_success

    def _device(self) -> ToyaDecoderDevice | None:
        """Return the matching device from coordinator data."""
        devices = self.coordinator.data
        if not devices:
            return None

        for device in devices:
            if device.smart_card == self._smart_card:
                return device
        return None

    def _resolve_channel_number(self, media_id: str) -> str | None:
        """Resolve a media id to a numeric channel string."""
        payload = str(media_id).strip()
        if payload.isdigit():
            return payload

        channel = self._channels.get(payload)
        if channel is not None and channel.number is not None:
            return str(channel.number)
        return None

    async def _send_keys(self, *keys: RemoteCommand) -> None:
        """Send one or more remote commands and refresh."""
        for key in keys:
            await self.coordinator.api.async_send_key(self._smart_card, key)

        await self.coordinator.async_request_refresh()

    async def _send_play_pause(self) -> None:
        """Send play/pause followed by OK."""
        await self._send_keys(RemoteCommand.PLAYPAUSE, RemoteCommand.OK)

    async def async_turn_on(self) -> None:
        """Send the power toggle if the device is currently off."""
        device = self._device()
        if device is not None and device.status == DeviceStatus.ON:
            return

        await self._send_keys(RemoteCommand.POWER)

    async def async_turn_off(self) -> None:
        """Send the power toggle if the device is currently on."""
        device = self._device()
        if device is not None and device.status == DeviceStatus.OFF:
            return

        await self._send_keys(RemoteCommand.POWER)

    async def async_volume_up(self) -> None:
        """Send volume up."""
        await self._send_keys(RemoteCommand.RIGHT)

    async def async_volume_down(self) -> None:
        """Send volume down."""
        await self._send_keys(RemoteCommand.LEFT)

    async def async_mute_volume(self, mute: bool) -> None:
        """Toggle mute (stateful mute is not supported by the API)."""
        await self._send_keys(RemoteCommand.MUTE)

    async def async_media_next_track(self) -> None:
        """Go to the next channel."""
        await self._send_keys(RemoteCommand.UP, RemoteCommand.FFW)

    async def async_media_previous_track(self) -> None:
        """Go to the previous channel."""
        await self._send_keys(RemoteCommand.DOWN, RemoteCommand.PREV)

    async def async_media_play_pause(self) -> None:
        """Toggle play/pause."""
        await self._send_play_pause()

    async def async_media_play(self) -> None:
        """Send play."""
        await self._send_play_pause()

    async def async_media_pause(self) -> None:
        """Send pause."""
        await self._send_play_pause()

    async def async_media_stop(self) -> None:
        """Send stop."""
        await self._send_keys(RemoteCommand.STOP)

    async def async_browse_media(
        self,
        media_content_type: str | None = None,
        media_content_id: str | None = None,
    ) -> BrowseMedia:
        """Build the media browser tree of available channels."""
        children: list[BrowseMedia] = [
            BrowseMedia(
                title=label,
                media_class=MediaClass.CHANNEL,
                media_content_id=str(channel.number),
                media_content_type=MediaType.CHANNEL,
                can_play=True,
                can_expand=False,
                thumbnail=channel.thumbnail,
            )
            for label, channel in self._channels.items()
        ]

        translations = await async_get_translations(
            self.hass,
            self.hass.config.language,
            "common",
            [DOMAIN],
        )
        title = translations.get(
            f"component.{DOMAIN}.common.channels", "Channels"
        )

        return BrowseMedia(
            title=title,
            media_class=MediaClass.DIRECTORY,
            media_content_id="channels",
            media_content_type=MediaType.CHANNEL,
            can_play=False,
            can_expand=True,
            children=children,
        )

    async def async_play_media(
        self, media_type: str, media_id: str, **kwargs
    ) -> None:
        """Tune to a channel by number or label."""
        channel_number = self._resolve_channel_number(media_id)
        if channel_number is None:
            _LOGGER.warning("Unknown media_id requested: %s", media_id)
            return

        await self.coordinator.api.async_set_channel(
            self._smart_card, channel_number
        )
        await self.coordinator.async_request_refresh()
