"""Custom exceptions for the Ento-Linguistic Research Project."""

from typing import Any, Dict, List, Optional

__all__ = [
    "ValidationError",
    "EntoLinguisticsError",
]


class EntoLinguisticsError(Exception):
    """Base class for Ento-Linguistic exceptions."""


class ValidationError(EntoLinguisticsError):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ):
        """Initialize validation error.

        Args:
            message: Error message
            context: Additional context information
            suggestions: Suggested actions to fix the error
        """
        self.message = message
        self.context = context or {}
        self.suggestions = suggestions or []

        super().__init__(message)
