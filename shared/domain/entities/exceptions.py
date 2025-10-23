"""Domain-level exceptions."""


class DomainError(Exception):
    """Base exception for domain errors."""


class DatabaseError(DomainError):
    """Database-related errors."""


class RateLimitError(DomainError):
    """Rate limiting errors."""


class ScraperError(DomainError):
    """Scraper-related errors."""


class ValidationError(DomainError):
    """Validation errors."""


class ConfigurationError(DomainError):
    """Configuration errors."""
