"""Exceptions for ConnectLife Cloud API client."""

from typing import Any


class ConnectLifeCloudError(Exception):
    """Base exception for ConnectLife Cloud API errors."""

    def __init__(self, message: str, details: Any = None) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.details = details


class ConnectLifeCloudAuthError(ConnectLifeCloudError):
    """Authentication related errors."""

    pass


class ConnectLifeCloudConnectionError(ConnectLifeCloudError):
    """Connection related errors."""

    pass


class ConnectLifeCloudAPIError(ConnectLifeCloudError):
    """API response related errors."""

    def __init__(self, message: str, status_code: int = None, response_data: Any = None) -> None:
        """Initialize the exception."""
        super().__init__(message, response_data)
        self.status_code = status_code
