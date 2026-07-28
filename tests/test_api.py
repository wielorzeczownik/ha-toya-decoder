"""Tests for the Toya decoder API client's handling of secrets."""

from __future__ import annotations

import pytest

from custom_components.toya_decoder.api import (
    ToyaDecoderApi,
    ToyaDecoderAuthError,
)
from custom_components.toya_decoder.api.auth import (
    extract_token,
    raise_if_auth_fault,
)

from .conftest import MOCK_PASSWORD, MOCK_USERNAME

MOCK_TOKEN = "tok-abc123"  # noqa: S105  # dummy credential for tests


def test_repr_carries_no_credentials() -> None:
    """The representation exposes neither credentials nor the session token."""
    api = ToyaDecoderApi(username=MOCK_USERNAME, password=MOCK_PASSWORD)
    api._token = MOCK_TOKEN  # noqa: SLF001  # exercising the redaction directly

    text = repr(api)

    assert MOCK_USERNAME not in text
    assert MOCK_PASSWORD not in text
    assert MOCK_TOKEN not in text
    assert "<redacted>" in text


def test_unparsable_auth_response_never_reaches_the_message() -> None:
    """A GetAuth response is a credential even when it cannot be parsed."""
    with pytest.raises(ToyaDecoderAuthError) as excinfo:
        extract_token({"unexpected": {"session": [None]}})

    assert "session" not in str(excinfo.value)
    assert "unexpected" not in str(excinfo.value)


def test_token_containing_base64_padding_survives_intact() -> None:
    """Nothing rewrites the credential; `=` is a legal token character."""
    padded = "c29tZS10b2tlbi12YWx1ZQ=="

    assert extract_token({"token": padded}) == padded


def test_status_like_response_does_not_become_a_token() -> None:
    """A response without a token field raises rather than inventing one."""
    with pytest.raises(ToyaDecoderAuthError):
        extract_token({"result": "OK"})


def test_upstream_fault_payload_never_reaches_the_message() -> None:
    """The upstream fault body stays out of the error the caller sees."""
    payload = {
        "faultCode": 2,
        "faultString": "User not authorised for account 12345",
    }

    with pytest.raises(ToyaDecoderAuthError) as excinfo:
        raise_if_auth_fault(payload)

    assert "12345" not in str(excinfo.value)
