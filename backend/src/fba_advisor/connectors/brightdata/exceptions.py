"""Exceptions raised by the Bright Data connector."""


class BrightDataConnectorError(Exception):
    """Base exception for Bright Data connector failures."""


class BrightDataAuthenticationError(BrightDataConnectorError):
    """Raised when Bright Data authentication credentials are invalid."""


class BrightDataAPIError(BrightDataConnectorError):
    """Raised when the Bright Data API returns an unsuccessful response."""


class BrightDataParsingError(BrightDataConnectorError):
    """Raised when a Bright Data response cannot be parsed."""
