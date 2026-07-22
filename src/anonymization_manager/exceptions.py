"""
Exception types for the anonymization manager.

All errors raised derive from the AnonymizationError class.
"""

class AnonymizationError(Exception):
    """
    Base class for all anonymization related errors.
    
    Attributes:
        message (str): The unformatted error message.
        backend (str | None): The backend that produced the error, if known.
            Included as a prefix in the formatted string representation.
    """

    def __init__(self, message: str, *, backend: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.backend = backend

    def __str__(self) -> str:
        base = super().__str__()
        return f"[{self.backend}] {base}" if self.backend else base

class ConfigurationError(AnonymizationError, ValueError):
    """
    Invalid or unsupported configuration.

    Raised before the anonymization process begins. These are user fixable
    errors in the AnonymizationConfig, e.g. unknown metric names, malformed parameters etc.
    """

class BackendError(AnonymizationError):
    """
    The underlying anonymization engine failed during execution.

    Errors of this kind occur at the anonymization phase, after a configuration was accepted but
    the anonymization backend crashed.
    """