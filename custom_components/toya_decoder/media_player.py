"""Media player entity for Toya decoder devices."""

from __future__ import annotations

import logging

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import ToyaDecoderChannel, ToyaDecoderDevice
from .const import (
    CONF_NAME,
    DEFAULT_NAME,
    DOMAIN,
    DeviceStatus,
    RemoteCommand,
    REMOTE_COMMANDS,
)
from .coordinator import ToyaDecoderCoordinator

try:
    from homeassistant.components.media_player.const import (
        MediaPlayerDeviceClass,
    )
except ImportError:
    MediaPlayerDeviceClass = None

try:
    from homeassistant.components.media_player.browse_media import BrowseMedia
    from homeassistant.components.media_player.const import (
        MediaClass,
        MediaType,
    )
except ImportError:
    BrowseMedia = None
    MediaClass = None
    MediaType = None

try:
    from homeassistant.helpers import translation as translation_helper
except ImportError:
    translation_helper = None

_LOGGER = logging.getLogger(__name__)


def _feature(*names: str) -> MediaPlayerEntityFeature:
    """Return a MediaPlayerEntityFeature mask built from names."""
    value = MediaPlayerEntityFeature(0)
    for name in names:
        if hasattr(MediaPlayerEntityFeature, name):
            value |= getattr(MediaPlayerEntityFeature, name)

    return value


_POWER_FEATURES = _feature("TURN_ON") | _feature("TURN_OFF")


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
        if channel.name:
            label = f"{number} {channel.name}"
        else:
            label = number

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

    base_name = entry.data.get(CONF_NAME) or DEFAULT_NAME
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


class ToyaLegacyDecoderMediaPlayer(CoordinatorEntity, MediaPlayerEntity):
    """Media player entity representing a Toya legacy decoder."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:television"
    if MediaPlayerDeviceClass is not None:
        _attr_device_class = MediaPlayerDeviceClass.TV

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
        self._attr_name = f"{base_name} {self._smart_card}"
        self.coordinator = coordinator
        self._attr_unique_id = f"toya_decoder_{entry_id}_{self._smart_card}"
        self._channels = channels

        self._attr_supported_features = (
            _POWER_FEATURES
            | _feature("VOLUME_STEP")
            | _feature("VOLUME_MUTE")
            | _feature("NEXT_TRACK")
            | _feature("PREVIOUS_TRACK")
            | _feature("PLAY")
            | _feature("PAUSE")
            | _feature("BROWSE_MEDIA")
            | _feature("PLAY_MEDIA")
        )

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Return supported features, masked by current device state."""
        features = self._attr_supported_features
        device = self._device()
        if device is None or device.status != DeviceStatus.ON:
            return features & ~_POWER_FEATURES

        return features

    @property
    def available(self) -> bool:
        """Return True when the coordinator last updated successfully."""

        return self.coordinator.last_update_success

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the media player state derived from device status."""
        device = self._device()
        if device is None:
            return MediaPlayerState.OFF

        return (
            MediaPlayerState.PLAYING
            if device.status == DeviceStatus.ON
            else MediaPlayerState.OFF
        )

    @property
    def media_content_type(self) -> str:
        """Return the content type shown in the media browser."""

        return "channel"

    @property
    def volume_level(self) -> float | None:
        """Return None because volume level is not reported."""

        return None

    @property
    def is_volume_muted(self) -> bool | None:
        """Return None because mute state is not reported."""

        return None

    @property
    def extra_state_attributes(self) -> dict[str, list[str] | str]:
        """Expose the smart card and available remote commands."""

        return {
            "smart_card": self._smart_card,
            "remote_commands": REMOTE_COMMANDS,
        }

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
    ) -> BrowseMedia | None:
        """Build the media browser tree of available channels."""
        if BrowseMedia is None:
            return None

        channel_class = (
            MediaClass.CHANNEL if MediaClass is not None else "channel"
        )
        channel_type = MediaType.CHANNEL if MediaType is not None else "channel"
        children: list[BrowseMedia] = []
        for label, channel in self._channels.items():
            channel_number = str(channel.number)
            children.append(
                BrowseMedia(
                    title=label,
                    media_class=channel_class,
                    media_content_id=channel_number,
                    media_content_type=channel_type,
                    can_play=True,
                    can_expand=False,
                    thumbnail=channel.thumbnail or None,
                )
            )

        root_class = (
            MediaClass.DIRECTORY if MediaClass is not None else "directory"
        )
        title = "Channels"
        if translation_helper is not None and self.hass is not None:
            translations = await translation_helper.async_get_translations(
                self.hass,
                self.hass.config.language,
                "media_browser",
                integrations=[DOMAIN],
            )
            title = translations.get(
                f"component.{DOMAIN}.media_browser.channels",
                title,
            )

        return BrowseMedia(
            title=title,
            media_class=root_class,
            media_content_id="channels",
            media_content_type=channel_type,
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
