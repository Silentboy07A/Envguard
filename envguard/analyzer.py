from .env import Env


class Analyzer:
    def __init__(self, env: Env):
        self.env = env

    def find_duplicates(self) -> list[str]:
        """Return duplicate variable names."""
        return list(dict.fromkeys(self.env.duplicates))

    def find_empty_values(self) -> list[str]:
        """Return variables with empty values."""
        empty = []

        for key in self.env.keys():
            if self.env.get_str(key) == "":
                empty.append(key)

        return empty

    def find_missing(self, required: list[str]) -> list[str]:
        """Return missing required variables."""
        missing = []

        for key in required:
            if not self.env.exists(key):
                missing.append(key)

        return missing

    def compare(self, example_env: Env) -> dict:
        """
        Compare current .env against .env.example.
        """

        current = set(self.env.keys())
        example = set(example_env.keys())

        return {
            "missing": sorted(example - current),
            "extra": sorted(current - example),
        }

    def summary(self, required: list[str] | None = None) -> dict:
        """
        Return a summary of all detected issues.
        """

        if required is None:
            required = []

        duplicates = self.find_duplicates()
        empty = self.find_empty_values()
        missing = self.find_missing(required)

        return {
            "duplicates": len(duplicates),
            "empty": len(empty),
            "missing": len(missing),
            "total": (
                len(duplicates)
                + len(empty)
                + len(missing)
            ),
        }