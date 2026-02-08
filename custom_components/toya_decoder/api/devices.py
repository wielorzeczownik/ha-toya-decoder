"""Device parsing helpers for the Toya decoder API client."""

from __future__ import annotations

import re
from typing import Any

from ..const import DeviceStatus
from .models import ToyaDecoderDevice


def parse_devices(res: Any) -> list[ToyaDecoderDevice]:
    """Parse device entries from GetPvrDevices responses."""
    if not res:
        return []

    devices: Any = res
    if isinstance(res, dict) and "devices" in res:
        devices = res["devices"]

    if isinstance(devices, (list, tuple)):
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

    raw = str(devices)
    raw = raw.strip()
    if (raw.startswith("[") and raw.endswith("]")) or (
        raw.startswith("{") and raw.endswith("}")
    ):
        raw = raw[1:-1]

    parts = [part for part in re.split(r"=|, |\}\{|\{|\}", raw) if part]
    out = []
    key = ""
    smart_card: str | None = None
    chip_id: str | None = None
    status: DeviceStatus | None = None

    for idx, part in enumerate(parts):
        if idx % 2 == 0:
            key = part
            continue

        value = part
        if key == "status":
            status = _status_from_value(value)
        elif key == "smartcard":
            smart_card = value
        elif key == "chipid":
            chip_id = value

        if (
            smart_card is not None
            and status is not None
            and chip_id is not None
        ):
            out.append(ToyaDecoderDevice(smart_card, status, chip_id=chip_id))
            smart_card = None
            chip_id = None
            status = None

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
