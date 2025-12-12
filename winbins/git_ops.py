"""
Git operations for WinBins.
Handles cloning, updating, and managing tool repositories.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class GitResult:
    """Result of a git operation."""
    success: bool
    output: str = ""
    error: str = ""
    return_code: int = 0


class GitOperations:
    """Handles git operations for tool repositories."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _run_git(self, args: List[str], cwd: Optional[Path] = None) -> GitResult:
        """Execute a git command and return result."""
        cmd = ["git"] + args
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
            )
            return GitResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                return_code=result.returncode,
            )
        except FileNotFoundError:
            return GitResult(
                success=False,
                error="git not found in PATH",
                return_code=-1,
            )
        except subprocess.SubprocessError as e:
            return GitResult(
                success=False,
                error=str(e),
                return_code=-1,
            )

    def is_git_available(self) -> bool:
        """Check if git is available on the system."""
        result = self._run_git(["--version"])
        return result.success

    def clone(self, repo_url: str, target_path: Path,
              branch: Optional[str] = None,
              depth: Optional[int] = None,
              recursive: bool = False) -> GitResult:
        """
        Clone a git repository.

        Args:
            repo_url: URL of the repository to clone
            target_path: Local path to clone to
            branch: Specific branch to clone
            depth: Shallow clone depth (None for full clone)
            recursive: Clone submodules recursively

        Returns:
            GitResult with success status and output
        """
        args = ["clone", repo_url, str(target_path)]

        if branch:
            args.extend(["-b", branch])

        if depth:
            args.extend(["--depth", str(depth)])

        if recursive:
            args.append("--recursive")

        return self._run_git(args)

    def fetch(self, repo_path: Path, remote: str = "origin",
              all_remotes: bool = False) -> GitResult:
        """
        Fetch updates from remote.

        Args:
            repo_path: Path to local repository
            remote: Remote name to fetch from
            all_remotes: Fetch from all remotes

        Returns:
            GitResult with success status
        """
        args = ["-C", str(repo_path), "fetch"]

        if all_remotes:
            args.append("--all")
        else:
            args.append(remote)

        return self._run_git(args)

    def reset(self, repo_path: Path, target: str = "origin/HEAD",
              hard: bool = True) -> GitResult:
        """
        Reset repository to a specific target.

        Args:
            repo_path: Path to local repository
            target: Target to reset to (branch, commit, tag)
            hard: Perform hard reset

        Returns:
            GitResult with success status
        """
        args = ["-C", str(repo_path), "reset"]

        if hard:
            args.append("--hard")

        args.append(target)
        return self._run_git(args)

    def clean(self, repo_path: Path, force: bool = True,
              directories: bool = True, ignored: bool = True) -> GitResult:
        """
        Clean untracked files from repository.

        Args:
            repo_path: Path to local repository
            force: Force removal
            directories: Remove directories
            ignored: Remove ignored files

        Returns:
            GitResult with success status
        """
        args = ["-C", str(repo_path), "clean"]

        if force:
            args.append("-f")
        if directories:
            args.append("-d")
        if ignored:
            args.append("-x")

        return self._run_git(args)

    def checkout(self, repo_path: Path, target: str) -> GitResult:
        """
        Checkout a branch or commit.

        Args:
            repo_path: Path to local repository
            target: Branch, tag, or commit to checkout

        Returns:
            GitResult with success status
        """
        return self._run_git(["-C", str(repo_path), "checkout", target])

    def pull(self, repo_path: Path, remote: str = "origin",
             branch: Optional[str] = None) -> GitResult:
        """
        Pull updates from remote.

        Args:
            repo_path: Path to local repository
            remote: Remote name
            branch: Branch to pull (None for current branch)

        Returns:
            GitResult with success status
        """
        args = ["-C", str(repo_path), "pull", remote]
        if branch:
            args.append(branch)
        return self._run_git(args)

    def get_current_branch(self, repo_path: Path) -> Optional[str]:
        """Get the current branch name."""
        result = self._run_git([
            "-C", str(repo_path),
            "rev-parse", "--abbrev-ref", "HEAD"
        ])
        if result.success:
            return result.output.strip()
        return None

    def get_latest_commit(self, repo_path: Path) -> Optional[str]:
        """Get the latest commit hash."""
        result = self._run_git([
            "-C", str(repo_path),
            "rev-parse", "HEAD"
        ])
        if result.success:
            return result.output.strip()
        return None

    def get_commit_date(self, repo_path: Path, commit: str = "HEAD") -> Optional[str]:
        """Get the date of a commit."""
        result = self._run_git([
            "-C", str(repo_path),
            "show", "-s", "--format=%ci", commit
        ])
        if result.success:
            return result.output.strip()
        return None

    def is_repo(self, path: Path) -> bool:
        """Check if path is a git repository."""
        result = self._run_git(["-C", str(path), "rev-parse", "--git-dir"])
        return result.success

    def clone_or_update(self, repo_url: str, target_path: Path,
                        branch: Optional[str] = None) -> GitResult:
        """
        Clone a repository if it doesn't exist, otherwise update it.

        Args:
            repo_url: URL of the repository
            target_path: Local path for the repository
            branch: Optional branch to use

        Returns:
            GitResult with success status
        """
        if target_path.exists() and self.is_repo(target_path):
            # Update existing repository
            result = self.fetch(target_path, all_remotes=True)
            if not result.success:
                return result

            target = f"origin/{branch}" if branch else "origin/HEAD"
            result = self.reset(target_path, target, hard=True)
            if not result.success:
                return result

            return self.clean(target_path)
        else:
            # Clone new repository
            return self.clone(repo_url, target_path, branch)


# Convenience functions
def clone_or_update(repo_url: str, target_path: Path,
                    branch: Optional[str] = None,
                    verbose: bool = False) -> GitResult:
    """Clone or update a repository."""
    ops = GitOperations(verbose)
    return ops.clone_or_update(repo_url, target_path, branch)
