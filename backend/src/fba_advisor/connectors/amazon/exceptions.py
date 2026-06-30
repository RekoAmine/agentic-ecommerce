"""Exceptions raised by the Amazon connector."""


class AmazonConnectorError(Exception):
    """Base exception for Amazon connector failures."""


class AmazonAuthenticationError(AmazonConnectorError):
    """Raised when Amazon authentication credentials are invalid."""


class AmazonAPIError(AmazonConnectorError):
    """Raised when the Amazon API returns an unsuccessful response."""


class AmazonParsingError(AmazonConnectorError):
    """Raised when an Amazon response cannot be parsed."""
