"""Centralized domain exceptions for the oort package."""


class Error(Exception):
    """Base exception for all oort domain errors."""

    pass


class S3ConfigurationError(Error):
    """Raised when S3 configuration is invalid or missing."""

    pass


class WebhookDispatchError(Error):
    """Raised when an error occurs during webhook dispatch."""

    pass


__all__ = ["Error", "S3ConfigurationError", "WebhookDispatchError"]
