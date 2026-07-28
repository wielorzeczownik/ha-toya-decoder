"""Channel parsing helpers for the Toya decoder API client."""

from __future__ import annotations

import html
import re
from functools import lru_cache
from typing import Any

from .models import ToyaDecoderChannel

_OBJECT_PATTERN = re.compile(
    r'<object\b[^>]*type="product"[^>]*id="([^"]+)"[^>]*>([\s\S]*?)</object>',
    re.IGNORECASE,
)


@lru_cache(maxsize=32)
def _attr_pattern(key: str) -> re.Pattern[str]:
    """Return the compiled pattern for one product attribute."""
    return re.compile(
        rf'<attr\b[^>]*key="{re.escape(key)}"[^>]*>'
        r"[\s\S]*?<value>([\s\S]*?)</value>",
        re.IGNORECASE,
    )


def extract_products_xml(res: Any) -> str:
    """Normalize GetProducts responses into a string XML payload."""
    if res is None:
        return ""

    if isinstance(res, bytes):
        return res.decode(errors="ignore")

    if isinstance(res, str):
        return res

    if isinstance(res, list):
        return "".join(str(item) for item in res)

    if isinstance(res, dict) and "products" in res:
        return extract_products_xml(res["products"])
    return str(res)


def _extract_attr_value(body: str, key: str) -> str | None:
    """Extract a product attribute value from the XML payload."""
    match = _attr_pattern(key).search(body)
    if not match:
        return None
    return html.unescape(match.group(1).strip())


def parse_channels(xml: str) -> list[ToyaDecoderChannel]:
    """Parse channel entries from the GetProducts XML body."""
    out: list[ToyaDecoderChannel] = []
    for match in _OBJECT_PATTERN.finditer(xml):
        channel_id = match.group(1)
        body = match.group(2)
        name = _extract_attr_value(body, "name") or _extract_attr_value(
            body, "shortTitle"
        )
        thumbnail = _extract_attr_value(body, "thumbnail")
        number_raw = (
            _extract_attr_value(body, "number")
            or _extract_attr_value(body, "channel_number")
            or _extract_attr_value(body, "lcn")
            or _extract_attr_value(body, "position")
        )
        number: int | None = None
        if number_raw:
            try:
                number = int(str(number_raw).strip())
            except ValueError:
                number = None

        out.append(
            ToyaDecoderChannel(
                id=channel_id,
                name=name,
                number=number,
                thumbnail=thumbnail,
            )
        )
    return out
