import pytest

from envguard.env import Env
from envguard.scanner import SecretScanner


def write_env(tmp_path, content: str):
    env_file = tmp_path / ".env"
    env_file.write_text(content)
    return env_file


def test_detect_openai_key(tmp_path):
    env_file = write_env(
        tmp_path,
        """
OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz123456789
"""
    )

    env = Env(env_file)
    scanner = SecretScanner(env)

    findings = scanner.scan()

    assert len(findings) == 1
    assert findings[0]["type"] == "OpenAI API Key"


def test_detect_aws_key(tmp_path):
    env_file = write_env(
        tmp_path,
        """
AWS_ACCESS_KEY=AKIA1234567890ABCDEF
"""
    )

    env = Env(env_file)
    scanner = SecretScanner(env)

    findings = scanner.scan()

    assert len(findings) == 1
    assert findings[0]["type"] == "AWS Access Key"


def test_detect_jwt(tmp_path):
    env_file = write_env(
        tmp_path,
        """
JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4ifQ.signature
"""
    )

    env = Env(env_file)
    scanner = SecretScanner(env)

    findings = scanner.scan()

    assert len(findings) == 1
    assert findings[0]["type"] == "JWT"


def test_high_entropy_string(tmp_path):
    env_file = write_env(
        tmp_path,
        """
SECRET=aB93Kd8LmPqX7RtVz1YnH4WuCe5FsGiJ
"""
    )

    env = Env(env_file)
    scanner = SecretScanner(env)

    findings = scanner.scan()

    assert any(
        finding["type"] == "High Entropy String"
        for finding in findings
    )


def test_no_secret_found(tmp_path):
    env_file = write_env(
        tmp_path,
        """
HOST=localhost
PORT=8000
DEBUG=true
"""
    )

    env = Env(env_file)
    scanner = SecretScanner(env)

    findings = scanner.scan()

    assert findings == []


def test_masking():
    scanner = SecretScanner(None)

    masked = scanner._mask(
        "abcdefghijklmnopqrstuvwxyz"
    )

    assert masked.startswith("abcd")
    assert masked.endswith("wxyz")
    assert "*" in masked