import math
import re

from .env import Env


class SecretScanner:
    PATTERNS = {
        "AWS Access Key": re.compile(r"AKIA[0-9A-Z]{16}"),
        "OpenAI API Key": re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        "GitHub Token": re.compile(r"ghp_[A-Za-z0-9]{36}"),
        "JWT": re.compile(
            r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"
        ),
        "Private Key": re.compile(
            r"-----BEGIN (RSA |EC |OPENSSH |)?PRIVATE KEY-----"
        ),
    }

    def __init__(self, env: Env):
        self.env = env

    def scan(self):
        findings = []

        for key in self.env.keys():
            value = self.env.get_str(key)

            matched = False

            for name, pattern in self.PATTERNS.items():
                if pattern.search(value):
                    findings.append(
                        {
                            "key": key,
                            "type": name,
                            "severity": "HIGH",
                            "value": self._mask(value),
                        }
                    )
                    matched = True

            # Only detect entropy if no known secret matched
            if not matched and self._high_entropy(value):
                findings.append(
                    {
                        "key": key,
                        "type": "High Entropy String",
                        "severity": "MEDIUM",
                        "value": self._mask(value),
                    }
                )

        return findings

    def _mask(self, value: str) -> str:
        if len(value) <= 8:
            return "*" * len(value)

        return value[:4] + "*" * (len(value) - 8) + value[-4:]

    def _high_entropy(self, value: str) -> bool:
        if len(value) < 20:
            return False

        entropy = self._entropy(value)
        return entropy > 4.0

    def _entropy(self, text: str) -> float:
        frequency = {}

        for char in text:
            frequency[char] = frequency.get(char, 0) + 1

        entropy = 0.0

        for count in frequency.values():
            probability = count / len(text)
            entropy -= probability * math.log2(probability)

        return entropy