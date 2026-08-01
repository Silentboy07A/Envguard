from pathlib import Path


class Env:
    def __init__(self, path: str = ".env"):
        self.path = Path(path)
        self._data = {}
        self._load()

    def _load(self):
        if not self.path.exists():
            raise FileNotFoundError(f"{self.path} not found")

        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                key, value = line.split("=", 1)
                self._data[key.strip()] = value.strip()

    def str(self, key: str):
        return self._data[key]

    def int(self, key: str):
        return int(self._data[key])

    def bool(self, key: str):
        value = self._data[key].lower()
        return value in ("true", "1", "yes", "on")