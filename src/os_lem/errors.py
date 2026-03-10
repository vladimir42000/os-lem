"""Project-specific exception types."""

class OSLemError(Exception):
    """Base class for os-lem errors."""


class SchemaError(OSLemError):
    """Raised when input schema is invalid."""


class ValidationError(OSLemError):
    """Raised when a structurally valid model is physically or topologically invalid."""


class NotImplementedKernelError(OSLemError):
    """Raised when the Session 4 scaffold reaches not-yet-implemented solver stages."""
