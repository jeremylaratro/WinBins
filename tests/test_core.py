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
