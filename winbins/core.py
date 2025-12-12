"""
Core WinToolsUpdater class for WinBins.
Orchestrates tool updates and builds.
"""

import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from winbins.logging import WinBinsLogger, LogLevel, get_logger
from winbins.git_ops import GitOperations, GitResult
from winbins.builders import get_builder, BuildResult
from winbins.tools.registry import ToolRegistry, TOOLS
from winbins.tools.base import ToolConfig


class WinToolsUpdater:
    """
    Main class for updating and building Windows pentesting tools.
    Coordinates git operations, builds, and artifact management.
    """

    def __init__(
        self,
        output_dir: str = "./binaries",
        build_dir: str = "./build",
        verbose: bool = False,
        logger: Optional[WinBinsLogger] = None,
        registry: Optional[ToolRegistry] = None,
    ):
        """
        Initialize the updater.

        Args:
            output_dir: Directory for compiled binaries
            build_dir: Directory for source code
            verbose: Enable verbose output
            logger: Custom logger instance
            registry: Custom tool registry
        """
        self.output_dir = Path(output_dir)
        self.build_dir = Path(build_dir)
        self.verbose = verbose

        # Initialize components
        self.logger = logger or get_logger(verbose)
        self.git = GitOperations(verbose)
        self.registry = registry or ToolRegistry()

        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def log(self, msg: str, level: str = "INFO") -> None:
        """Log a message (for backwards compatibility)."""
        level_map = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
            "SUCCESS": LogLevel.SUCCESS,
        }
        self.logger.log(msg, level_map.get(level, LogLevel.INFO))

    def run_cmd(self, cmd: List[str], cwd: Optional[Path] = None) -> bool:
        """Execute command and return success status (for backwards compatibility)."""
        import subprocess
        try:
            if self.verbose:
                self.log(f"Running: {' '.join(cmd)}", "DEBUG")

            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=not self.verbose,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {' '.join(cmd)}", "ERROR")
            if self.verbose and e.stderr:
                self.log(e.stderr, "ERROR")
            return False
        except FileNotFoundError:
            self.log(f"Command not found: {cmd[0]}", "ERROR")
            return False

    def check_dependencies(self, tool_name: str, tool_config: Dict[str, Any]) -> bool:
        """Check if build dependencies are available."""
        required = tool_config.get("requires")
        if not required:
            return True

        if shutil.which(required) is None:
            self.log(f"Missing dependency for {tool_name}: {required}", "ERROR")
            return False
        return True

    def clone_or_update(self, tool_name: str, repo_url: str,
                        branch: Optional[str] = None) -> Optional[Path]:
        """Clone or update a tool's git repository."""
        tool_path = self.build_dir / tool_name

        if tool_path.exists():
            self.log(f"Updating {tool_name}...")
        else:
            self.log(f"Cloning {tool_name}...")

        result = self.git.clone_or_update(repo_url, tool_path, branch)

        if not result.success:
            self.log(f"Git operation failed: {result.error}", "ERROR")
            return None

        return tool_path

    def build_tool(self, tool_name: str, tool_config: Dict[str, Any],
                   tool_path: Path) -> bool:
        """Build the tool from source."""
        self.log(f"Building {tool_name}...")

        # Get appropriate builder
        builder = get_builder(
            tool_config.get("requires", "msbuild"),
            verbose=self.verbose,
            env_vars=tool_config.get("env_vars", {})
        )

        if builder and builder.is_available():
            result = builder.build(
                tool_path,
                tool_config["build_cmd"],
                tool_config["output"]
            )

            if result.failed:
                self.log(f"Build failed: {result.error_message}", "ERROR")
                return False

            # Copy to output directory
            if result.output_path:
                dest_path = self.output_dir / result.output_path.name
                if builder.copy_artifact(result.output_path, dest_path):
                    self.log(f"Built {tool_name} -> {dest_path}", "SUCCESS")
                    return True
                else:
                    self.log(f"Failed to copy artifact to {dest_path}", "ERROR")
                    return False
        else:
            # Fallback to direct command execution
            build_cmd = tool_config["build_cmd"]
            if not self.run_cmd(build_cmd, cwd=tool_path):
                return False

            # Copy output to final location
            output_path = tool_path / tool_config["output"]
            if not output_path.exists():
                self.log(f"Build artifact not found: {output_path}", "ERROR")
                return False

            dest_path = self.output_dir / output_path.name
            shutil.copy2(output_path, dest_path)
            self.log(f"Built {tool_name} -> {dest_path}", "SUCCESS")
            return True

        return False

    def update_tool(self, tool_name: str, branch: Optional[str] = None) -> bool:
        """Update and build a single tool."""
        # Try registry first, fall back to TOOLS dict for backwards compatibility
        tool = self.registry.get(tool_name)
        if tool:
            tool_config = tool.to_dict()
        elif tool_name in TOOLS:
            tool_config = TOOLS[tool_name]
        else:
            self.log(f"Unknown tool: {tool_name}", "ERROR")
            return False

        # Check dependencies
        if not self.check_dependencies(tool_name, tool_config):
            return False

        # Clone/update repository
        tool_path = self.clone_or_update(tool_name, tool_config["repo"], branch)
        if not tool_path:
            return False

        # Build
        return self.build_tool(tool_name, tool_config, tool_path)

    def update_all(self, branch: Optional[str] = None,
                   tools: Optional[List[str]] = None) -> Dict[str, bool]:
        """Update specified tools or all tools."""
        tools_to_update = tools if tools else self.registry.list_tools()
        results = {}

        for tool_name in tools_to_update:
            self.log(f"\n{'='*60}")
            self.log(f"Processing: {tool_name.upper()}")
            self.log(f"{'='*60}")

            success = self.update_tool(tool_name, branch)
            results[tool_name] = success

        return results

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool."""
        tool = self.registry.get(tool_name)
        if tool:
            info = tool.to_dict()
            # Add build status if we have the tool built
            output_path = self.output_dir / Path(tool.output).name
            info["built"] = output_path.exists()
            if output_path.exists():
                info["built_path"] = str(output_path)
            return info
        return None

    def list_tools(self) -> List[str]:
        """List all available tools."""
        return self.registry.list_tools()

    def list_built_tools(self) -> List[str]:
        """List tools that have been built."""
        built = []
        for tool_name in self.registry.list_tools():
            tool = self.registry.get(tool_name)
            if tool:
                output_path = self.output_dir / Path(tool.output).name
                if output_path.exists():
                    built.append(tool_name)
        return built
