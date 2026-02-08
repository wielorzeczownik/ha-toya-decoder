"""Small utility helpers for the API client."""

from __future__ import annotations

import hashlib
import os
import socket

from ..const import REMOTE_COMMANDS
from .errors import ToyaDecoderApiError


def build_device_id() -> str:
    """Build a deterministic device id for the API session."""
    base = f"{socket.gethostname()}|{os.getcwd()}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]

    return f"ha-{digest}"


def normalize_cmd(key: str) -> str:
    """Normalize and validate command names."""
    text = str(key).strip()
    if len(text) == 1 and text.isdigit():
        return text

    cmd = text.lower()
    if cmd in REMOTE_COMMANDS:
        return cmd

    raise ToyaDecoderApiError(f"Unsupported command: {key}")
