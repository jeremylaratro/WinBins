"""
Base builder interface for WinBins.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import shutil
import subprocess


@dataclass
class BuildResult:
    """Result of a build operation."""
    success: bool
    output_path: Optional[Path] = None
    stdout: str = ""
    stderr: str = ""
    return_code: int = 0
    error_message: str = ""
    artifacts: List[Path] = field(default_factory=list)

    @property
    def failed(self) -> bool:
        """Check if build failed."""
        return not self.success


class Builder(ABC):
    """Abstract base class for build systems."""

    def __init__(self, verbose: bool = False, env_vars: Optional[Dict[str, str]] = None):
        self.verbose = verbose
        self.env_vars = env_vars or {}

    @property
    @abstractmethod
    def name(self) -> str:
        """Return builder name."""
        pass

    @property
    @abstractmethod
    def executable(self) -> str:
        """Return the executable name for this build system."""
        pass

    def is_available(self) -> bool:
        """Check if the build tool is available on the system."""
        return shutil.which(self.executable) is not None

    @abstractmethod
    def build(self, source_path: Path, build_cmd: List[str],
              output_path: str) -> BuildResult:
        """
        Execute the build.

        Args:
            source_path: Path to source code
            build_cmd: Build command to execute
            output_path: Relative path to expected output

        Returns:
            BuildResult with success status and output details
        """
        pass

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None,
                    capture: bool = True) -> BuildResult:
        """Execute a command and return the result."""
        try:
            import os
            env = os.environ.copy()
            env.update(self.env_vars)

            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=capture,
                text=True,
                env=env,
            )

            return BuildResult(
                success=result.returncode == 0,
                stdout=result.stdout if capture else "",
                stderr=result.stderr if capture else "",
                return_code=result.returncode,
            )
        except FileNotFoundError:
            return BuildResult(
                success=False,
                error_message=f"Command not found: {cmd[0]}",
                return_code=-1,
            )
        except subprocess.SubprocessError as e:
            return BuildResult(
                success=False,
                error_message=str(e),
                return_code=-1,
            )

    def copy_artifact(self, source: Path, dest: Path) -> bool:
        """Copy build artifact to destination."""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            return True
        except (shutil.Error, OSError):
            return False
