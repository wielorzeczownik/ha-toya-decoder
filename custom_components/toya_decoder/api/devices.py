"""Device parsing helpers for the Toya decoder API client."""

from __future__ import annotations

from typing import Any

from custom_components.toya_decoder.const import DeviceStatus

from .models import ToyaDecoderDevice


def parse_devices(res: Any) -> list[ToyaDecoderDevice]:
    """Parse device entries from GetPvrDevices responses."""
    if not res:
        return []

    devices: Any = res
    if isinstance(res, dict) and "devices" in res:
        devices = res["devices"]

    if isinstance(devices, (list, tuple)):
        return _parse_structured_devices(devices)

    return []


def _parse_structured_devices(
    devices: list[Any] | tuple[Any, ...],
) -> list[ToyaDecoderDevice]:
    """Parse devices from a list of mapping entries."""
    out: list[ToyaDecoderDevice] = []
    for item in devices:
        if not isinstance(item, dict):
            continue

        smart_card = item.get("smartcard")
        chip_id = item.get("chipid")
        status = item.get("status", 0)
        if smart_card and chip_id is not None:
            out.append(
                ToyaDecoderDevice(
                    str(smart_card),
                    _status_from_value(status),
                    str(chip_id),
                )
            )
    return out


def _safe_int(value: Any) -> int:
    """Convert to int or return 0."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _status_from_value(value: Any) -> DeviceStatus:
    """Convert status values to DeviceStatus enum."""
    numeric = _safe_int(value)
    try:
        return DeviceStatus(numeric)
    except ValueError:
        return DeviceStatus.UNKNOWN
