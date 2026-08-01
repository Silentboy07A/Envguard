import pytest

from envguard.env import Env
from envguard.analyzer import Analyzer


def write_env(tmp_path, content: str):
    env_file = tmp_path / ".env"
    env_file.write_text(content)
    return env_file


def test_find_duplicates(tmp_path):
    env_file = write_env(
        tmp_path,
        """
HOST=localhost
PORT=8000
PORT=9000
"""
    )

    env = Env(env_file)
    analyzer = Analyzer(env)

    assert analyzer.find_duplicates() == ["PORT"]


def test_find_empty_values(tmp_path):
    env_file = write_env(
        tmp_path,
        """
HOST=localhost
API_KEY=
PORT=8000
"""
    )

    env = Env(env_file)
    analyzer = Analyzer(env)

    assert analyzer.find_empty_values() == ["API_KEY"]


def test_find_missing(tmp_path):
    env_file = write_env(
        tmp_path,
        """
HOST=localhost
PORT=8000
"""
    )

    env = Env(env_file)
    analyzer = Analyzer(env)

    required = ["HOST", "PORT", "DATABASE_URL"]

    assert analyzer.find_missing(required) == ["DATABASE_URL"]


def test_compare(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        """
HOST=localhost
PORT=8000
SECRET=abc
"""
    )

    example_file = tmp_path / ".env.example"
    example_file.write_text(
        """
HOST=
PORT=
DATABASE_URL=
"""
    )

    env = Env(env_file)
    example = Env(example_file)

    analyzer = Analyzer(env)

    result = analyzer.compare(example)

    assert result["missing"] == ["DATABASE_URL"]
    assert result["extra"] == ["SECRET"]


def test_summary(tmp_path):
    env_file = write_env(
        tmp_path,
        """
HOST=localhost
API_KEY=
PORT=8000
PORT=9000
"""
    )

    env = Env(env_file)
    analyzer = Analyzer(env)

    summary = analyzer.summary(
        ["HOST", "PORT", "DATABASE_URL"]
    )

    assert summary["duplicates"] == 1
    assert summary["empty"] == 1
    assert summary["missing"] == 1
    assert summary["total"] == 3