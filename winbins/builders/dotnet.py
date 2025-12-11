"""
.NET CLI builder implementation for WinBins.
"""

from pathlib import Path
from typing import Dict, List, Optional

from winbins.builders.base import Builder, BuildResult


class DotNetBuilder(Builder):
    """Builder for .NET SDK projects."""

    def __init__(self, verbose: bool = False, env_vars: Optional[Dict[str, str]] = None,
                 configuration: str = "Release", framework: Optional[str] = None,
                 runtime: Optional[str] = None):
        super().__init__(verbose, env_vars)
        self.configuration = configuration
        self.framework = framework
        self.runtime = runtime

    @property
    def name(self) -> str:
        return "DotNet"

    @property
    def executable(self) -> str:
        return "dotnet"

    def build(self, source_path: Path, build_cmd: List[str],
              output_path: str) -> BuildResult:
        """
        Build a .NET project using dotnet CLI.

        Args:
            source_path: Path to source code containing .csproj/.sln file
            build_cmd: Build command (typically ["dotnet", "build", ...])
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

    def get_default_build_cmd(self, project_file: Optional[str] = None,
                               publish: bool = False) -> List[str]:
        """Generate default build/publish command."""
        action = "publish" if publish else "build"
        cmd = [self.executable, action, "-c", self.configuration]

        if project_file:
            cmd.insert(2, project_file)

        if self.framework:
            cmd.extend(["-f", self.framework])

        if self.runtime and publish:
            cmd.extend(["-r", self.runtime])

        return cmd

    def restore(self, source_path: Path) -> BuildResult:
        """Restore NuGet packages."""
        return self.run_command(
            [self.executable, "restore"],
            cwd=source_path,
            capture=not self.verbose
        )

    def publish(self, source_path: Path, build_cmd: List[str],
                output_path: str) -> BuildResult:
        """
        Publish a .NET project for deployment.
        Creates a self-contained executable when runtime is specified.
        """
        # Modify build command for publish
        publish_cmd = build_cmd.copy()
        if publish_cmd[1] == "build":
            publish_cmd[1] = "publish"
        elif "publish" not in publish_cmd:
            publish_cmd.insert(1, "publish")

        return self.build(source_path, publish_cmd, output_path)
