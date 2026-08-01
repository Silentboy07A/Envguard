from pathlib import Path
import re
from typing import Iterator
from .exceptions import (
    EnvFileNotFoundError,
    EnvParseError,
    MissingVariableError,
    InvalidBooleanError,
    InvalidIntegerError,
)

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


class Env:
    TRUE_VALUES = {"true", "1", "yes", "on"}
    FALSE_VALUES = {"false", "0", "no", "off"}

    KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    def __init__(self, path: str = ".env"):
        self.path = Path(path)
        self._data = {}
        self.duplicates = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            raise EnvFileNotFoundError(f"{self.path} not found")

        with self.path.open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise EnvParseError(
                        f"Invalid syntax at line {line_number}: {line}"
                    )

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if not self.KEY_PATTERN.fullmatch(key):
                    raise EnvParseError(
                        f"Invalid variable name '{key}' at line {line_number}"
                    )

                # Handle quoted values first
                is_quoted = (
                    len(value) >= 2
                    and value[0] == value[-1]
                    and value[0] in ("'", '"')
                )

                if is_quoted:
                    value = value[1:-1]
                elif " #" in value:
                    value = value.split(" #", 1)[0].rstrip()

                if key in self._data:
                    self.duplicates.append(key)

                self._data[key] = {
                    "value": value,
                    "file": str(self.path),
                    "line": line_number,
                }

    def exists(self, key: str) -> bool:
        return key in self._data

    def get_str(self, key: str) -> str:
        if key not in self._data:
            raise MissingVariableError(f"{key} not found")

        return self._data[key]["value"]

    def get_int(self, key: str) -> int:
        raw = self.get_str(key)

        try:
            return int(raw)
        except ValueError as exc:
            raise InvalidIntegerError(
                f"Invalid integer value '{raw}' for '{key}'"
            ) from exc

    def get_bool(self, key: str) -> bool:
        value = self.get_str(key).lower()

        if value in self.TRUE_VALUES:
            return True

        if value in self.FALSE_VALUES:
            return False

        raise InvalidBooleanError(
            f"Invalid boolean value '{value}' for '{key}'"
        )

    def keys(self):
        return self._data.keys()

    def values(self) -> Iterator[str]:
        for meta in self._data.values():
            yield meta["value"]

    def items(self) -> Iterator[tuple[str, str]]:
        for key, meta in self._data.items():
            yield key, meta["value"]

    def explain(self, key: str) -> dict:
        if key not in self._data:
            raise MissingVariableError(f"{key} not found")

        return self._data[key]