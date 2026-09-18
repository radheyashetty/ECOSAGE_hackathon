"""Custom exceptions for EcoSage."""
from typing import Any


class EcoSageError(Exception):
    """Base exception for all EcoSage runtime errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(EcoSageError):
    """Raised when environment or configuration is invalid."""


class KnowledgeBaseError(EcoSageError):
    """Raised when knowledge base access, indexing, or retrieval fails."""


class LLMGenerationError(EcoSageError):
    """Raised when LLM calls fail across all provider fallbacks."""


class ValidationError(EcoSageError):
    """Raised when recommendations fail the scientific validation checks."""


class ServiceUnavailableError(EcoSageError):
    """Raised when external AI services are unreachable."""
