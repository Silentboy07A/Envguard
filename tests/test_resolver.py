import pytest

from envguard.env import Env
from envguard.resolver import Resolver
from envguard.exceptions import (
    CircularReferenceError,
    UndefinedVariableError,
)


def write_env(tmp_path, content: str):
    env_file = tmp_path / ".env"
    env_file.write_text(content)
    return env_file


def test_simple_resolution(tmp_path):
    env_file = write_env(
        tmp_path,
        """
HOST=localhost
PORT=8000
URL=http://${HOST}:${PORT}
"""
    )

    env = Env(env_file)
    resolver = Resolver(env)

    result = resolver.resolve_all()

    assert result["URL"] == "http://localhost:8000"


def test_nested_resolution(tmp_path):
    env_file = write_env(
        tmp_path,
        """
HOST=localhost
PORT=8000
URL=http://${HOST}:${PORT}
API=${URL}/api
"""
    )

    env = Env(env_file)
    resolver = Resolver(env)

    result = resolver.resolve_all()

    assert result["API"] == "http://localhost:8000/api"


def test_undefined_variable(tmp_path):
    env_file = write_env(
        tmp_path,
        """
URL=http://${HOST}
"""
    )

    env = Env(env_file)
    resolver = Resolver(env)

    with pytest.raises(UndefinedVariableError):
        resolver.resolve_all()


def test_circular_reference(tmp_path):
    env_file = write_env(
        tmp_path,
        """
A=${B}
B=${A}
"""
    )

    env = Env(env_file)
    resolver = Resolver(env)

    with pytest.raises(CircularReferenceError):
        resolver.resolve_all()


def test_no_variables(tmp_path):
    env_file = write_env(
        tmp_path,
        """
HOST=localhost
PORT=8000
"""
    )

    env = Env(env_file)
    resolver = Resolver(env)

    result = resolver.resolve_all()

    assert result["HOST"] == "localhost"
    assert result["PORT"] == "8000"