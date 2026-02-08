"""Exceptions for the Toya decoder API client."""


class ToyaDecoderApiError(Exception):
    """General API error."""


class ToyaDecoderConnectionError(ToyaDecoderApiError):
    """Connection or transport error."""


class ToyaDecoderAuthError(ToyaDecoderApiError):
    """Authentication failed."""
