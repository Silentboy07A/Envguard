import re

from .env import Env
from .exceptions import (
    CircularReferenceError,
    UndefinedVariableError,
)


class Resolver:
    VARIABLE_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")

    def __init__(self, env: Env):
        self.env = env
        self._resolved = {}

    def resolve_all(self):
        for key in self.env.keys():
            self.resolve(key)

        return self._resolved

    def resolve(self, key: str):
        return self._resolve(key, set())

    def _resolve(self, key: str, visited: set):
        if key in self._resolved:
            return self._resolved[key]

        if key in visited:
            raise CircularReferenceError(
                f"Circular reference detected: {key}"
            )

        if not self.env.exists(key):
            raise UndefinedVariableError(
                f"Undefined variable: {key}"
            )

        visited.add(key)

        value = self.env.get_str(key)

        def replace(match):
            variable = match.group(1)
            return self._resolve(variable, visited)

        value = self.VARIABLE_PATTERN.sub(replace, value)

        visited.remove(key)

        self._resolved[key] = value

        return value