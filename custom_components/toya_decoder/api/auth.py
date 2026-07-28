"""Authentication helpers for the Toya decoder API client."""

from __future__ import annotations

import logging
from typing import Any

from .errors import ToyaDecoderAuthError

_LOGGER = logging.getLogger(__name__)


def _normalize_token(raw: str) -> str:
    """Strip surrounding whitespace and quoting from a token string."""
    token = raw.strip()
    if len(token) >= 2 and token.startswith('"') and token.endswith('"'):
        token = token[1:-1]
    return token


# GetAuth answers with {"token": "<26 chars>"}
_TOKEN_KEYS = ("token", "authToken", "auth")


def _extract_token_from_value(res: Any) -> str | None:
    """Find the token in a GetAuth response."""
    if isinstance(res, str):
        return _normalize_token(res) or None

    if isinstance(res, dict):
        for key in _TOKEN_KEYS:
            value = res.get(key)
            if isinstance(value, str):
                token = _normalize_token(value)
                if token:
                    return token
        return None

    if isinstance(res, (list, tuple)):
        for item in res:
            nested = _extract_token_from_value(item)
            if nested:
                return nested

    return None


def extract_token(res: Any) -> str:
    """Extract a token from a GetAuth response or raise on failure."""
    token = _extract_token_from_value(res)
    if not token:
        raise ToyaDecoderAuthError("Unexpected GetAuth response")
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
        _LOGGER.debug("Auth fault in response: %r", res)
        raise ToyaDecoderAuthError("User not authorised")
