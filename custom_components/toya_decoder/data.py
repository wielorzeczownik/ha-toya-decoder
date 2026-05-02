"""Runtime data types for the Toya decoder integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .api import ToyaDecoderApi
    from .coordinator import ToyaDecoderCoordinator


@dataclass
class ToyaDecoderData:
    """Runtime data stored in ConfigEntry.runtime_data."""

    api: ToyaDecoderApi
    coordinator: ToyaDecoderCoordinator
