"""
Tests for the core module.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

from winbins.core import WinToolsUpdater
from winbins.tools.registry import ToolRegistry


class TestWinToolsUpdater:
    """Tests for WinToolsUpdater class."""

    def test_init_creates_directories(self, temp_dir):
        """Test that init creates output and build directories."""
        output = temp_dir / "output"
        build = temp_dir / "build"

        updater = WinToolsUpdater(str(output), str(build))

        assert output.exists()
        assert build.exists()

    def test_init_with_custom_registry(self, temp_dir, sample_tools):
        """Test init with custom tool registry."""
        registry = ToolRegistry(tools=sample_tools)
        updater = WinToolsUpdater(
            str(temp_dir / "output"),
            str(temp_dir / "build"),
            registry=registry
        )

        assert updater.registry is registry
        assert "tool1" in updater.list_tools()

    def test_list_tools(self, temp_dir):
        """Test listing available tools."""
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        tools = updater.list_tools()

        assert isinstance(tools, list)
        assert "rubeus" in tools

    def test_get_tool_info(self, temp_dir):
        """Test getting tool information."""
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        info = updater.get_tool_info("rubeus")

        assert info is not None
        assert "repo" in info
        assert "GhostPack/Rubeus" in info["repo"]

    def test_get_tool_info_nonexistent(self, temp_dir):
        """Test getting info for non-existent tool."""
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        info = updater.get_tool_info("nonexistent")

        assert info is None

    @patch("shutil.which")
    def test_check_dependencies_available(self, mock_which, temp_dir):
        """Test dependency check when available."""
        mock_which.return_value = "/usr/bin/msbuild"
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))

        result = updater.check_dependencies("test", {"requires": "msbuild"})

        assert result is True

    @patch("shutil.which")
    def test_check_dependencies_missing(self, mock_which, temp_dir):
        """Test dependency check when missing."""
        mock_which.return_value = None
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))

        result = updater.check_dependencies("test", {"requires": "msbuild"})

        assert result is False

    def test_check_dependencies_none_required(self, temp_dir):
        """Test dependency check when none required."""
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))

        result = updater.check_dependencies("test", {})

        assert result is True

    @patch("subprocess.run")
    def test_run_cmd_success(self, mock_run, temp_dir):
        """Test running command successfully."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success",
            stderr="",
        )
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))

        result = updater.run_cmd(["echo", "test"])

        assert result is True

    @patch("subprocess.run")
    def test_run_cmd_failure(self, mock_run, temp_dir):
        """Test running command that fails."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, ["false"])
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))

        result = updater.run_cmd(["false"])

        assert result is False

    @patch.object(WinToolsUpdater, "clone_or_update")
    @patch.object(WinToolsUpdater, "check_dependencies")
    @patch.object(WinToolsUpdater, "build_tool")
    def test_update_tool_success(self, mock_build, mock_deps, mock_clone, temp_dir):
        """Test successful tool update."""
        mock_deps.return_value = True
        mock_clone.return_value = temp_dir / "build" / "rubeus"
        mock_build.return_value = True

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        result = updater.update_tool("rubeus")

        assert result is True
        mock_deps.assert_called_once()
        mock_clone.assert_called_once()
        mock_build.assert_called_once()

    @patch.object(WinToolsUpdater, "check_dependencies")
    def test_update_tool_missing_deps(self, mock_deps, temp_dir):
        """Test tool update with missing dependencies."""
        mock_deps.return_value = False

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        result = updater.update_tool("rubeus")

        assert result is False

    def test_update_tool_unknown(self, temp_dir):
        """Test updating unknown tool."""
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        result = updater.update_tool("nonexistent_tool")

        assert result is False

    @patch.object(WinToolsUpdater, "update_tool")
    def test_update_all(self, mock_update, temp_dir):
        """Test updating all tools."""
        mock_update.return_value = True

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        results = updater.update_all()

        assert isinstance(results, dict)
        assert all(v is True for v in results.values())

    @patch.object(WinToolsUpdater, "update_tool")
    def test_update_all_specific_tools(self, mock_update, temp_dir):
        """Test updating specific tools."""
        mock_update.return_value = True

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        results = updater.update_all(tools=["rubeus", "seatbelt"])

        assert len(results) == 2
        assert "rubeus" in results
        assert "seatbelt" in results

    @patch.object(WinToolsUpdater, "update_tool")
    def test_update_all_partial_failure(self, mock_update, temp_dir):
        """Test update_all with partial failures."""
        mock_update.side_effect = [True, False, True]

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        results = updater.update_all(tools=["tool1", "tool2", "tool3"])

        assert results["tool1"] is True
        assert results["tool2"] is False
        assert results["tool3"] is True


class TestWinToolsUpdaterIntegration:
    """Integration tests for WinToolsUpdater."""

    @patch("winbins.git_ops.GitOperations.clone_or_update")
    @patch("winbins.builders.get_builder")
    @patch("shutil.which")
    def test_full_update_flow(self, mock_which, mock_get_builder, mock_git, temp_dir):
        """Test full update flow with mocks."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/msbuild"

        from winbins.git_ops import GitResult
        mock_git.return_value = GitResult(success=True)

        mock_builder = MagicMock()
        mock_builder.is_available.return_value = True
        from winbins.builders.base import BuildResult
        mock_builder.build.return_value = BuildResult(
            success=True,
            output_path=temp_dir / "tool.exe"
        )
        mock_builder.copy_artifact.return_value = True
        mock_get_builder.return_value = mock_builder

        # Create fake output file
        (temp_dir / "tool.exe").touch()

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))

        # This would normally run the full flow
        # For now, just verify the updater is properly configured
        assert updater.output_dir.exists()
        assert updater.build_dir.exists()


class TestWinToolsUpdaterBuildTool:
    """Tests for WinToolsUpdater.build_tool method."""

    @patch("winbins.core.get_builder")
    def test_build_tool_with_builder(self, mock_get_builder, temp_dir):
        """Test building tool with available builder."""
        mock_builder = MagicMock()
        mock_builder.is_available.return_value = True
        from winbins.builders.base import BuildResult
        output_file = temp_dir / "build" / "rubeus" / "Rubeus.exe"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.touch()
        mock_builder.build.return_value = BuildResult(
            success=True,
            output_path=output_file
        )
        mock_builder.copy_artifact.return_value = True
        mock_get_builder.return_value = mock_builder

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        tool_config = {
            "requires": "msbuild",
            "build_cmd": ["msbuild", "Rubeus.sln"],
            "output": "Rubeus.exe",
        }

        result = updater.build_tool("rubeus", tool_config, temp_dir / "build" / "rubeus")

        assert result is True
        mock_builder.build.assert_called_once()

    @patch("winbins.core.get_builder")
    def test_build_tool_copy_failure(self, mock_get_builder, temp_dir):
        """Test building tool when copy fails."""
        mock_builder = MagicMock()
        mock_builder.is_available.return_value = True
        from winbins.builders.base import BuildResult
        output_file = temp_dir / "build" / "rubeus" / "Rubeus.exe"
        mock_builder.build.return_value = BuildResult(
            success=True,
            output_path=output_file
        )
        mock_builder.copy_artifact.return_value = False
        mock_get_builder.return_value = mock_builder

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        tool_config = {
            "requires": "msbuild",
            "build_cmd": ["msbuild", "Rubeus.sln"],
            "output": "Rubeus.exe",
        }

        result = updater.build_tool("rubeus", tool_config, temp_dir / "build" / "rubeus")

        assert result is False

    @patch("winbins.core.get_builder")
    def test_build_tool_build_failure(self, mock_get_builder, temp_dir):
        """Test building tool when build fails."""
        mock_builder = MagicMock()
        mock_builder.is_available.return_value = True
        from winbins.builders.base import BuildResult
        mock_builder.build.return_value = BuildResult(
            success=False,
            error_message="Build failed"
        )
        mock_get_builder.return_value = mock_builder

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        tool_config = {
            "requires": "msbuild",
            "build_cmd": ["msbuild", "Rubeus.sln"],
            "output": "Rubeus.exe",
        }

        result = updater.build_tool("rubeus", tool_config, temp_dir / "build" / "rubeus")

        assert result is False

    @patch("winbins.core.get_builder")
    @patch("subprocess.run")
    def test_build_tool_fallback(self, mock_run, mock_get_builder, temp_dir):
        """Test building tool with fallback when builder unavailable."""
        mock_get_builder.return_value = None
        mock_run.return_value = MagicMock(returncode=0)

        # Create tool directory and output file
        tool_path = temp_dir / "build" / "rubeus"
        tool_path.mkdir(parents=True)
        (tool_path / "Rubeus.exe").touch()

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        tool_config = {
            "requires": "msbuild",
            "build_cmd": ["msbuild", "Rubeus.sln"],
            "output": "Rubeus.exe",
        }

        result = updater.build_tool("rubeus", tool_config, tool_path)

        assert result is True

    @patch("winbins.core.get_builder")
    @patch("subprocess.run")
    def test_build_tool_fallback_output_missing(self, mock_run, mock_get_builder, temp_dir):
        """Test building tool with fallback when output missing."""
        mock_get_builder.return_value = None
        mock_run.return_value = MagicMock(returncode=0)

        tool_path = temp_dir / "build" / "rubeus"
        tool_path.mkdir(parents=True)
        # Don't create output file

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        tool_config = {
            "requires": "msbuild",
            "build_cmd": ["msbuild", "Rubeus.sln"],
            "output": "Rubeus.exe",
        }

        result = updater.build_tool("rubeus", tool_config, tool_path)

        assert result is False


class TestWinToolsUpdaterCloneOrUpdate:
    """Tests for WinToolsUpdater.clone_or_update method."""

    @patch("winbins.git_ops.GitOperations.clone_or_update")
    def test_clone_new_repo(self, mock_git, temp_dir):
        """Test cloning a new repository."""
        from winbins.git_ops import GitResult
        mock_git.return_value = GitResult(success=True)

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        result = updater.clone_or_update(
            "rubeus",
            "https://github.com/test/repo.git"
        )

        assert result is not None
        assert result == updater.build_dir / "rubeus"

    @patch("winbins.git_ops.GitOperations.clone_or_update")
    def test_clone_failure(self, mock_git, temp_dir):
        """Test clone failure."""
        from winbins.git_ops import GitResult
        mock_git.return_value = GitResult(success=False, error="Clone failed")

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        result = updater.clone_or_update(
            "rubeus",
            "https://github.com/test/repo.git"
        )

        assert result is None

    @patch("winbins.git_ops.GitOperations.clone_or_update")
    def test_update_existing_repo(self, mock_git, temp_dir):
        """Test updating an existing repository."""
        from winbins.git_ops import GitResult
        mock_git.return_value = GitResult(success=True)

        # Create existing repo directory
        (temp_dir / "build" / "rubeus").mkdir(parents=True)

        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        result = updater.clone_or_update(
            "rubeus",
            "https://github.com/test/repo.git"
        )

        assert result is not None


class TestWinToolsUpdaterListBuiltTools:
    """Tests for WinToolsUpdater.list_built_tools method."""

    def test_list_built_tools_none(self, temp_dir):
        """Test listing built tools when none are built."""
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))
        built = updater.list_built_tools()

        assert isinstance(built, list)
        assert len(built) == 0

    def test_list_built_tools_some(self, temp_dir):
        """Test listing built tools when some are built."""
        output_dir = temp_dir / "out"
        output_dir.mkdir(parents=True)

        # Create fake built tool
        (output_dir / "Rubeus.exe").touch()

        updater = WinToolsUpdater(str(output_dir), str(temp_dir / "build"))
        built = updater.list_built_tools()

        assert "rubeus" in built


class TestWinToolsUpdaterVerbose:
    """Tests for verbose mode."""

    @patch("subprocess.run")
    def test_run_cmd_verbose(self, mock_run, temp_dir):
        """Test running command in verbose mode."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success",
            stderr="",
        )
        updater = WinToolsUpdater(
            str(temp_dir / "out"),
            str(temp_dir / "build"),
            verbose=True
        )

        result = updater.run_cmd(["echo", "test"])

        assert result is True
        # In verbose mode, capture_output should be False
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["capture_output"] is False

    @patch("subprocess.run")
    def test_run_cmd_command_not_found(self, mock_run, temp_dir):
        """Test running command that doesn't exist."""
        mock_run.side_effect = FileNotFoundError()
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))

        result = updater.run_cmd(["nonexistent"])

        assert result is False

    @patch("subprocess.run")
    def test_run_cmd_failure_with_stderr(self, mock_run, temp_dir):
        """Test running command that fails with stderr output."""
        import subprocess
        error = subprocess.CalledProcessError(1, ["cmd"])
        error.stderr = "Error message"
        mock_run.side_effect = error

        updater = WinToolsUpdater(
            str(temp_dir / "out"),
            str(temp_dir / "build"),
            verbose=True
        )

        result = updater.run_cmd(["cmd"])

        assert result is False


class TestWinToolsUpdaterLog:
    """Tests for logging functionality."""

    def test_log_with_different_levels(self, temp_dir):
        """Test logging with different log levels."""
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))

        # These should not raise
        updater.log("Debug message", "DEBUG")
        updater.log("Info message", "INFO")
        updater.log("Warning message", "WARNING")
        updater.log("Error message", "ERROR")
        updater.log("Success message", "SUCCESS")

    def test_log_with_unknown_level(self, temp_dir):
        """Test logging with unknown log level defaults to INFO."""
        updater = WinToolsUpdater(str(temp_dir / "out"), str(temp_dir / "build"))

        # Should not raise, defaults to INFO
        updater.log("Unknown level message", "UNKNOWN")
