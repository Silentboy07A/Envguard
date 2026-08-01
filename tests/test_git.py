import subprocess

from envguard.git import GitIntegration


def test_is_git_repo():
    git = GitIntegration()
    assert isinstance(git.is_git_repo(), bool)


def test_status():
    git = GitIntegration()

    status = git.status()

    assert "git_repository" in status
    assert "env_tracked" in status
    assert "env_ignored" in status


def test_add_to_gitignore(tmp_path):
    git = GitIntegration(tmp_path)

    assert git.add_to_gitignore(".env") is True
    assert git.is_ignored(".env") is True

    # Second call should not duplicate the entry
    assert git.add_to_gitignore(".env") is False