"""
MSBuild builder implementation for WinBins.
"""

from pathlib import Path
from typing import Dict, List, Optional

from winbins.builders.base import Builder, BuildResult


class MSBuildBuilder(Builder):
    """Builder for MSBuild-based projects (Visual Studio solutions)."""

    def __init__(self, verbose: bool = False, env_vars: Optional[Dict[str, str]] = None,
                 configuration: str = "Release", platform: Optional[str] = None):
        super().__init__(verbose, env_vars)
        self.configuration = configuration
        self.platform = platform

    @property
    def name(self) -> str:
        return "MSBuild"

    @property
    def executable(self) -> str:
        return "msbuild"

    def build(self, source_path: Path, build_cmd: List[str],
              output_path: str) -> BuildResult:
        """
        Build a Visual Studio solution using MSBuild.

        Args:
            source_path: Path to source code containing .sln file
            build_cmd: Build command (typically ["msbuild", "Project.sln", ...])
            output_path: Relative path to expected output binary

        Returns:
            BuildResult with success status and output details
        """
        if not self.is_available():
            return BuildResult(
                success=False,
                error_message=f"{self.executable} not found in PATH"
            )

        # Execute build command
        result = self.run_command(build_cmd, cwd=source_path, capture=not self.verbose)

        if result.failed:
            return result

        # Verify output exists
        full_output_path = source_path / output_path
        if not full_output_path.exists():
            return BuildResult(
                success=False,
                error_message=f"Build artifact not found: {full_output_path}",
                stdout=result.stdout,
                stderr=result.stderr,
            )

        result.success = True
        result.output_path = full_output_path
        result.artifacts = [full_output_path]
        return result

    def get_default_build_cmd(self, solution_file: str) -> List[str]:
        """Generate default build command for a solution file."""
        cmd = [
            self.executable,
            solution_file,
            f"/p:Configuration={self.configuration}",
        ]
        if self.platform:
            cmd.append(f"/p:Platform={self.platform}")
        return cmd
