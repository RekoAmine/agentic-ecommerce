"""Exceptions raised by the Keepa connector."""


class KeepaConnectorError(Exception):
    """Base exception for Keepa connector failures."""


class KeepaAuthenticationError(KeepaConnectorError):
    """Raised when Keepa authentication credentials are invalid."""


class KeepaAPIError(KeepaConnectorError):
    """Raised when the Keepa API returns an unsuccessful response."""


class KeepaParsingError(KeepaConnectorError):
    """Raised when a Keepa response cannot be parsed."""
