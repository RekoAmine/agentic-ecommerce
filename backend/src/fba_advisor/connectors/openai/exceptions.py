"""Exceptions raised by the OpenAI connector."""


class OpenAIConnectorError(Exception):
    """Base exception for OpenAI connector failures."""


class OpenAIAuthenticationError(OpenAIConnectorError):
    """Raised when OpenAI authentication credentials are invalid."""


class OpenAIAPIError(OpenAIConnectorError):
    """Raised when the OpenAI API returns an unsuccessful response."""


class OpenAIParsingError(OpenAIConnectorError):
    """Raised when a OpenAI response cannot be parsed."""
