"""Authentication helpers for the Toya decoder API client."""

from __future__ import annotations

import json
from typing import Any

from .errors import ToyaDecoderAuthError


def _format_response(res: Any) -> str:
    """Format a response for diagnostic messages."""
    try:
        return json.dumps(res)
    except TypeError:
        return repr(res)


def _normalize_token(raw: str) -> str:
    """Normalize token strings returned by XML-RPC responses."""
    token = raw.strip()
    if not token:
        return token

    parts = token.split("=")
    if len(parts) >= 2:
        token = "=".join(parts[1:]).strip()

    if token.endswith(";"):
        token = token[:-1].strip()

    if token.startswith('"') and token.endswith('"') and len(token) >= 2:
        token = token[1:-1]

    return token


def _extract_token_from_value(res: Any) -> str | None:
    """Search nested response structures for a token-like value."""
    if res is None:
        return None

    if isinstance(res, (str, int, bool)):
        token = _normalize_token(str(res))

        return token or None

    if isinstance(res, (list, tuple)):
        for item in res:
            token = _extract_token_from_value(item)
            if token:
                return token

        return None

    if isinstance(res, dict):
        for key in (
            "token",
            "auth",
            "authToken",
            "authorization",
            "result",
            "value",
        ):
            if key in res:
                token = _extract_token_from_value(res[key])
                if token:
                    return token

        values = list(res.values())
        if len(values) == 1:
            return _extract_token_from_value(values[0])

    return None


def extract_token(res: Any) -> str:
    """Extract a token from a GetAuth response or raise on failure."""
    token = _extract_token_from_value(res)
    if not token:
        raise ToyaDecoderAuthError(
            f"Unexpected GetAuth response: {_format_response(res)}"
        )

    return token


def _extract_fault_payload(res: Any) -> tuple[str | int | None, str | None]:
    """Extract fault code and message from XML-RPC responses."""
    if isinstance(res, dict):
        code = (
            res.get("faultCode")
            or res.get("faultcode")
            or res.get("fault_code")
        )
        text = (
            res.get("faultString")
            or res.get("faultstring")
            or res.get("fault_string")
            or res.get("message")
        )

        return code, str(text) if text is not None else None

    if isinstance(res, (list, tuple)):
        for item in res:
            code, text = _extract_fault_payload(item)
            if code is not None or text:
                return code, text

    return None, None


def is_auth_fault_message(text: str | None) -> bool:
    """Return True for fault messages that indicate auth failure."""
    if not text:
        return False

    lowered = text.lower()

    return "not author" in lowered or "unauthor" in lowered


def _is_auth_fault(res: Any) -> bool:
    """Return True when the response encodes an auth failure."""
    code, text = _extract_fault_payload(res)
    if code is None and not text:
        return False

    if is_auth_fault_message(text):
        return True

    return str(code) == "2"


def raise_if_auth_fault(res: Any) -> None:
    """Raise an auth error if the response contains an auth fault."""
    if _is_auth_fault(res):
        raise ToyaDecoderAuthError(
            f"User not authorised: {_format_response(res)}"
        )
