from pathlib import Path
import subprocess


class GitIntegration:
    def __init__(self, repo: str = "."):
        self.repo = Path(repo)

    def _run(self, *args):
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo,
            capture_output=True,
            text=True,
        )
        return result

    def is_git_repo(self) -> bool:
        result = self._run("rev-parse", "--is-inside-work-tree")
        return result.returncode == 0

    def is_tracked(self, file: str) -> bool:
        result = self._run("ls-files", "--error-unmatch", file)
        return result.returncode == 0

    def is_ignored(self, file: str) -> bool:
        gitignore = self.repo / ".gitignore"

        if not gitignore.exists():
            return False

        entries = {
            line.strip()
            for line in gitignore.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }

        return file in entries

    def add_to_gitignore(self, file: str = ".env") -> bool:
        gitignore = self.repo / ".gitignore"

        if gitignore.exists():
            content = gitignore.read_text(encoding="utf-8").splitlines()
        else:
            content = []

        if file in content:
            return False

        with gitignore.open("a", encoding="utf-8") as f:
            if content:
                f.write("\n")
            f.write(file + "\n")

        return True

    def remove_from_index(self, file: str) -> bool:
        result = self._run("rm", "--cached", file)
        return result.returncode == 0

    def status(self):
        return {
            "git_repository": self.is_git_repo(),
            "env_tracked": self.is_tracked(".env"),
            "env_ignored": self.is_ignored(".env"),
        }