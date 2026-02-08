"""Data models for the Toya decoder API client."""

from __future__ import annotations

from dataclasses import dataclass

from ..const import DeviceStatus


@dataclass
class ToyaDecoderState:
    """Represents the overall power state of the decoder."""

    is_on: bool = False


@dataclass
class ToyaDecoderDevice:
    """Represents a decoder device entry from the API."""

    smart_card: str
    status: DeviceStatus
    chip_id: str


@dataclass
class ToyaDecoderChannel:
    """Represents a broadcast channel entry from the API."""

    id: str
    number: int | None
    name: str | None
    thumbnail: str | None
