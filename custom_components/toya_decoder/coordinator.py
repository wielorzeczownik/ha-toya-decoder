"""Data update coordinator for Toya decoder devices."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import ToyaDecoderApi, ToyaDecoderDevice
from .const import DEFAULT_POLL_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ToyaDecoderCoordinator(DataUpdateCoordinator[list[ToyaDecoderDevice]]):
    """Coordinator that refreshes device state from the API."""

    def __init__(self, hass: HomeAssistant, api: ToyaDecoderApi) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_coordinator",
            update_interval=timedelta(seconds=DEFAULT_POLL_INTERVAL),
        )
        self.api = api

    async def _async_update_data(self) -> list[ToyaDecoderDevice]:
        """Fetch the latest device list from the API."""
        try:
            return await self.api.async_get_devices()
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(str(err)) from err
