class EnvError(Exception):
    """Base exception for EnvGuard."""


class EnvFileNotFoundError(EnvError):
    """Raised when the .env file is not found."""


class EnvParseError(EnvError):
    """Raised when the .env file contains invalid syntax."""


class MissingVariableError(EnvError):
    """Raised when a requested variable does not exist."""


class InvalidBooleanError(EnvError):
    """Raised when a boolean value is invalid."""


class InvalidIntegerError(EnvError):
    """Raised when an integer value is invalid."""


class CircularReferenceError(EnvError):
    """Raised when circular variable references are detected."""


class UndefinedVariableError(EnvError):
    """Raised when a referenced variable is undefined."""