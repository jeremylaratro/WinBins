"""
Tests for the git_ops module.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from winbins.git_ops import GitOperations, GitResult, clone_or_update


class TestGitResult:
    """Tests for GitResult dataclass."""

    def test_success_result(self):
        """Test successful git result."""
        result = GitResult(success=True, output="Done")
        assert result.success is True
        assert result.output == "Done"
        assert result.return_code == 0

    def test_failed_result(self):
        """Test failed git result."""
        result = GitResult(success=False, error="Failed", return_code=128)
        assert result.success is False
        assert result.error == "Failed"
        assert result.return_code == 128


class TestGitOperations:
    """Tests for GitOperations class."""

    @patch("subprocess.run")
    def test_is_git_available_true(self, mock_run):
        """Test git availability when installed."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="git version 2.40.0",
            stderr="",
        )
        git = GitOperations()
        assert git.is_git_available() is True

    @patch("subprocess.run")
    def test_is_git_available_false(self, mock_run):
        """Test git availability when not installed."""
        mock_run.side_effect = FileNotFoundError()
        git = GitOperations()
        assert git.is_git_available() is False

    @patch("subprocess.run")
    def test_clone_basic(self, mock_run):
        """Test basic clone operation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        result = git.clone(
            "https://github.com/test/repo.git",
            Path("/tmp/repo")
        )

        assert result.success is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "git" in call_args
        assert "clone" in call_args
        assert "https://github.com/test/repo.git" in call_args

    @patch("subprocess.run")
    def test_clone_with_branch(self, mock_run):
        """Test clone with specific branch."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        result = git.clone(
            "https://github.com/test/repo.git",
            Path("/tmp/repo"),
            branch="develop"
        )

        call_args = mock_run.call_args[0][0]
        assert "-b" in call_args
        assert "develop" in call_args

    @patch("subprocess.run")
    def test_clone_with_depth(self, mock_run):
        """Test shallow clone."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        result = git.clone(
            "https://github.com/test/repo.git",
            Path("/tmp/repo"),
            depth=1
        )

        call_args = mock_run.call_args[0][0]
        assert "--depth" in call_args
        assert "1" in call_args

    @patch("subprocess.run")
    def test_clone_recursive(self, mock_run):
        """Test recursive clone."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        result = git.clone(
            "https://github.com/test/repo.git",
            Path("/tmp/repo"),
            recursive=True
        )

        call_args = mock_run.call_args[0][0]
        assert "--recursive" in call_args

    @patch("subprocess.run")
    def test_fetch(self, mock_run):
        """Test fetch operation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        result = git.fetch(Path("/tmp/repo"))

        assert result.success is True
        call_args = mock_run.call_args[0][0]
        assert "fetch" in call_args

    @patch("subprocess.run")
    def test_fetch_all(self, mock_run):
        """Test fetch all remotes."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        result = git.fetch(Path("/tmp/repo"), all_remotes=True)

        call_args = mock_run.call_args[0][0]
        assert "--all" in call_args

    @patch("subprocess.run")
    def test_reset_hard(self, mock_run):
        """Test hard reset operation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        result = git.reset(Path("/tmp/repo"), "origin/main", hard=True)

        assert result.success is True
        call_args = mock_run.call_args[0][0]
        assert "reset" in call_args
        assert "--hard" in call_args
        assert "origin/main" in call_args

    @patch("subprocess.run")
    def test_clean(self, mock_run):
        """Test clean operation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        result = git.clean(Path("/tmp/repo"))

        assert result.success is True
        call_args = mock_run.call_args[0][0]
        assert "clean" in call_args
        assert "-f" in call_args
        assert "-d" in call_args
        assert "-x" in call_args

    @patch("subprocess.run")
    def test_checkout(self, mock_run):
        """Test checkout operation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        result = git.checkout(Path("/tmp/repo"), "develop")

        assert result.success is True
        call_args = mock_run.call_args[0][0]
        assert "checkout" in call_args
        assert "develop" in call_args

    @patch("subprocess.run")
    def test_pull(self, mock_run):
        """Test pull operation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        result = git.pull(Path("/tmp/repo"))

        assert result.success is True
        call_args = mock_run.call_args[0][0]
        assert "pull" in call_args

    @patch("subprocess.run")
    def test_get_current_branch(self, mock_run):
        """Test getting current branch."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="main\n",
            stderr="",
        )
        git = GitOperations()

        branch = git.get_current_branch(Path("/tmp/repo"))

        assert branch == "main"

    @patch("subprocess.run")
    def test_get_latest_commit(self, mock_run):
        """Test getting latest commit hash."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123def456\n",
            stderr="",
        )
        git = GitOperations()

        commit = git.get_latest_commit(Path("/tmp/repo"))

        assert commit == "abc123def456"

    @patch("subprocess.run")
    def test_is_repo_true(self, mock_run):
        """Test checking if path is a repo - true case."""
        mock_run.return_value = MagicMock(returncode=0, stdout=".git", stderr="")
        git = GitOperations()

        assert git.is_repo(Path("/tmp/repo")) is True

    @patch("subprocess.run")
    def test_is_repo_false(self, mock_run):
        """Test checking if path is a repo - false case."""
        mock_run.return_value = MagicMock(returncode=128, stdout="", stderr="")
        git = GitOperations()

        assert git.is_repo(Path("/tmp/not_a_repo")) is False

    @patch("subprocess.run")
    def test_clone_or_update_new(self, mock_run, temp_dir):
        """Test clone_or_update when repo doesn't exist."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        target = temp_dir / "new_repo"
        result = git.clone_or_update(
            "https://github.com/test/repo.git",
            target
        )

        assert result.success is True
        # Should have called clone
        call_args = mock_run.call_args[0][0]
        assert "clone" in call_args

    @patch("subprocess.run")
    def test_clone_or_update_existing(self, mock_run, temp_dir):
        """Test clone_or_update when repo exists."""
        # Create a fake repo directory
        repo_path = temp_dir / "existing_repo"
        repo_path.mkdir()
        (repo_path / ".git").mkdir()

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        git = GitOperations()

        result = git.clone_or_update(
            "https://github.com/test/repo.git",
            repo_path
        )

        # Should have called fetch, reset, clean (not clone)
        calls = [str(call) for call in mock_run.call_args_list]
        assert any("fetch" in str(call) for call in calls)


class TestCloneOrUpdateFunction:
    """Tests for clone_or_update convenience function."""

    @patch("subprocess.run")
    def test_clone_or_update(self, mock_run, temp_dir):
        """Test convenience function."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        target = temp_dir / "repo"
        result = clone_or_update(
            "https://github.com/test/repo.git",
            target
        )

        assert result.success is True
