"""
Tests for the CLI module.
"""

import pytest
import json
from pathlib import Path
from io import StringIO
from unittest.mock import MagicMock, patch, call

from winbins.cli import (
    create_parser,
    list_tools,
    check_dependencies,
    run_update,
    main,
)
from winbins.tools.registry import ToolRegistry
from winbins.tools.base import ToolCategory


class TestCreateParser:
    """Tests for create_parser function."""

    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "winbins"

    def test_parser_has_version(self):
        """Test that parser has version argument."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])

    def test_parser_output_default(self):
        """Test default output directory."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.output == "./binaries"

    def test_parser_output_custom(self):
        """Test custom output directory."""
        parser = create_parser()
        args = parser.parse_args(["-o", "/custom/path"])
        assert args.output == "/custom/path"

    def test_parser_build_dir_default(self):
        """Test default build directory."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.build_dir == "./build"

    def test_parser_build_dir_custom(self):
        """Test custom build directory."""
        parser = create_parser()
        args = parser.parse_args(["-b", "/custom/build"])
        assert args.build_dir == "/custom/build"

    def test_parser_tools(self):
        """Test specifying tools."""
        parser = create_parser()
        args = parser.parse_args(["-t", "rubeus", "seatbelt"])
        assert args.tools == ["rubeus", "seatbelt"]

    def test_parser_branch(self):
        """Test specifying branch."""
        parser = create_parser()
        args = parser.parse_args(["--branch", "develop"])
        assert args.branch == "develop"

    def test_parser_verbose(self):
        """Test verbose flag."""
        parser = create_parser()
        args = parser.parse_args(["-v"])
        assert args.verbose is True

    def test_parser_list(self):
        """Test list flag."""
        parser = create_parser()
        args = parser.parse_args(["--list"])
        assert args.list is True

    def test_parser_category(self):
        """Test category filter."""
        parser = create_parser()
        args = parser.parse_args(["--category", "credential_access"])
        assert args.category == "credential_access"

    def test_parser_search(self):
        """Test search argument."""
        parser = create_parser()
        args = parser.parse_args(["--search", "kerberos"])
        assert args.search == "kerberos"

    def test_parser_config(self):
        """Test config file argument."""
        parser = create_parser()
        args = parser.parse_args(["-c", "config.yaml"])
        assert args.config == "config.yaml"

    def test_parser_check_deps(self):
        """Test check-deps flag."""
        parser = create_parser()
        args = parser.parse_args(["--check-deps"])
        assert args.check_deps is True


class TestListTools:
    """Tests for list_tools function."""

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_all_tools(self, mock_stdout):
        """Test listing all tools."""
        registry = ToolRegistry()
        result = list_tools(registry)

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Available Tools:" in output
        assert "rubeus" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_tools_by_category(self, mock_stdout):
        """Test listing tools by category."""
        registry = ToolRegistry()
        result = list_tools(registry, category="credential_access")

        assert result == 0
        output = mock_stdout.getvalue()
        assert "rubeus" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_tools_by_search(self, mock_stdout):
        """Test listing tools by search."""
        registry = ToolRegistry()
        result = list_tools(registry, search="kerberos")

        assert result == 0
        output = mock_stdout.getvalue()
        assert "rubeus" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_tools_search_no_results(self, mock_stdout):
        """Test listing tools with search that finds nothing."""
        registry = ToolRegistry()
        result = list_tools(registry, search="nonexistent_tool_xyz")

        assert result == 1
        output = mock_stdout.getvalue()
        assert "No tools found" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_tools_category_no_results(self, mock_stdout):
        """Test listing tools with empty category."""
        registry = ToolRegistry(tools={})
        result = list_tools(registry, category="credential_access")

        assert result == 1
        output = mock_stdout.getvalue()
        assert "No tools found" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_tools_shows_details(self, mock_stdout):
        """Test that tool details are shown."""
        registry = ToolRegistry()
        result = list_tools(registry)

        output = mock_stdout.getvalue()
        assert "Description:" in output
        assert "Repository:" in output
        assert "Requires:" in output
        assert "Category:" in output


class TestCheckDependencies:
    """Tests for check_dependencies function."""

    @patch("winbins.builders.BuilderFactory.list_available")
    @patch("winbins.git_ops.GitOperations.is_git_available")
    @patch("sys.stdout", new_callable=StringIO)
    def test_check_deps_all_available(self, mock_stdout, mock_git, mock_builders):
        """Test dependency check when all available."""
        mock_builders.return_value = {"msbuild": True, "dotnet": True}
        mock_git.return_value = True

        registry = ToolRegistry()
        result = check_dependencies(registry)

        output = mock_stdout.getvalue()
        assert "Build Dependencies Status:" in output
        assert "[+]" in output

    @patch("winbins.builders.BuilderFactory.list_available")
    @patch("winbins.git_ops.GitOperations.is_git_available")
    @patch("sys.stdout", new_callable=StringIO)
    def test_check_deps_missing(self, mock_stdout, mock_git, mock_builders):
        """Test dependency check when some missing."""
        mock_builders.return_value = {"msbuild": False, "dotnet": False}
        mock_git.return_value = False

        registry = ToolRegistry()
        result = check_dependencies(registry)

        assert result == 1
        output = mock_stdout.getvalue()
        assert "[-]" in output
        assert "MISSING" in output

    @patch("winbins.builders.BuilderFactory.list_available")
    @patch("winbins.git_ops.GitOperations.is_git_available")
    @patch("sys.stdout", new_callable=StringIO)
    def test_check_deps_shows_tool_status(self, mock_stdout, mock_git, mock_builders):
        """Test that tool availability is shown."""
        mock_builders.return_value = {"msbuild": True, "dotnet": False}
        mock_git.return_value = True

        registry = ToolRegistry()
        check_dependencies(registry)

        output = mock_stdout.getvalue()
        assert "Tool Availability:" in output
        assert "Can build:" in output


class TestRunUpdate:
    """Tests for run_update function."""

    @patch("winbins.cli.WinToolsUpdater")
    @patch("sys.stdout", new_callable=StringIO)
    def test_run_update_basic(self, mock_stdout, mock_updater_class):
        """Test basic update run."""
        mock_updater = MagicMock()
        mock_updater.update_all.return_value = {"rubeus": True}
        mock_updater.output_dir = MagicMock()
        mock_updater.output_dir.absolute.return_value = "/test/output"
        mock_updater_class.return_value = mock_updater

        parser = create_parser()
        args = parser.parse_args(["-t", "rubeus"])

        result = run_update(args)

        assert result == 0
        mock_updater.update_all.assert_called_once()

    @patch("winbins.cli.WinToolsUpdater")
    @patch("sys.stdout", new_callable=StringIO)
    def test_run_update_with_failures(self, mock_stdout, mock_updater_class):
        """Test update run with failures."""
        mock_updater = MagicMock()
        mock_updater.update_all.return_value = {"rubeus": True, "seatbelt": False}
        mock_updater.output_dir = MagicMock()
        mock_updater.output_dir.absolute.return_value = "/test/output"
        mock_updater_class.return_value = mock_updater

        parser = create_parser()
        args = parser.parse_args(["-t", "rubeus", "seatbelt"])

        result = run_update(args)

        assert result == 1
        output = mock_stdout.getvalue()
        assert "+ SUCCESS" in output
        assert "- FAILED" in output

    @patch("winbins.cli.WinToolsUpdater")
    @patch("sys.stdout", new_callable=StringIO)
    def test_run_update_unknown_tool(self, mock_stdout, mock_updater_class):
        """Test update run with unknown tool."""
        parser = create_parser()
        args = parser.parse_args(["-t", "nonexistent_tool"])

        result = run_update(args)

        assert result == 1
        output = mock_stdout.getvalue()
        assert "[ERROR]" in output
        assert "Unknown tool" in output

    @patch("winbins.cli.WinToolsUpdater")
    @patch("winbins.cli.load_config")
    @patch("sys.stdout", new_callable=StringIO)
    def test_run_update_with_config(self, mock_stdout, mock_load_config, mock_updater_class):
        """Test update run with config file."""
        mock_config = MagicMock()
        mock_config.output_dir = "/config/output"
        mock_config.build_dir = "/config/build"
        mock_config.tools = {}
        mock_load_config.return_value = mock_config

        mock_updater = MagicMock()
        mock_updater.update_all.return_value = {}
        mock_updater.output_dir = MagicMock()
        mock_updater.output_dir.absolute.return_value = "/config/output"
        mock_updater_class.return_value = mock_updater

        parser = create_parser()
        args = parser.parse_args(["-c", "config.yaml"])

        run_update(args)

        # Verify config was used
        mock_updater_class.assert_called_once()
        call_kwargs = mock_updater_class.call_args[1]
        assert call_kwargs["output_dir"] == "/config/output"

    @patch("winbins.cli.WinToolsUpdater")
    @patch("winbins.cli.load_config")
    @patch("sys.stdout", new_callable=StringIO)
    def test_run_update_with_config_tools(self, mock_stdout, mock_load_config, mock_updater_class):
        """Test update run with custom tools from config."""
        mock_config = MagicMock()
        mock_config.output_dir = "./binaries"
        mock_config.build_dir = "./build"
        mock_config.tools = {
            "custom_tool": {
                "repo": "https://github.com/test/custom.git",
                "build_cmd": ["make"],
                "output": "bin/custom",
                "requires": "make",
            }
        }
        mock_load_config.return_value = mock_config

        mock_updater = MagicMock()
        mock_updater.update_all.return_value = {}
        mock_updater.output_dir = MagicMock()
        mock_updater.output_dir.absolute.return_value = "./binaries"
        mock_updater_class.return_value = mock_updater

        parser = create_parser()
        args = parser.parse_args(["-c", "config.yaml", "-t", "custom_tool"])

        result = run_update(args)

        # Should succeed because custom_tool is in config
        assert result == 0


class TestMain:
    """Tests for main function."""

    @patch("winbins.cli.list_tools")
    def test_main_list(self, mock_list_tools):
        """Test main with --list flag."""
        mock_list_tools.return_value = 0

        result = main(["--list"])

        assert result == 0
        mock_list_tools.assert_called_once()

    @patch("winbins.cli.list_tools")
    def test_main_search(self, mock_list_tools):
        """Test main with --search flag."""
        mock_list_tools.return_value = 0

        result = main(["--search", "kerberos"])

        assert result == 0
        mock_list_tools.assert_called_once()

    @patch("winbins.cli.check_dependencies")
    def test_main_check_deps(self, mock_check_deps):
        """Test main with --check-deps flag."""
        mock_check_deps.return_value = 0

        result = main(["--check-deps"])

        assert result == 0
        mock_check_deps.assert_called_once()

    @patch("winbins.cli.run_update")
    def test_main_update(self, mock_run_update):
        """Test main runs update by default."""
        mock_run_update.return_value = 0

        result = main([])

        assert result == 0
        mock_run_update.assert_called_once()

    @patch("winbins.cli.run_update")
    def test_main_with_tools(self, mock_run_update):
        """Test main with specific tools."""
        mock_run_update.return_value = 0

        result = main(["-t", "rubeus", "seatbelt"])

        assert result == 0
        args = mock_run_update.call_args[0][0]
        assert args.tools == ["rubeus", "seatbelt"]

    @patch("winbins.cli.run_update")
    def test_main_with_verbose(self, mock_run_update):
        """Test main with verbose flag."""
        mock_run_update.return_value = 0

        result = main(["-v"])

        assert result == 0
        args = mock_run_update.call_args[0][0]
        assert args.verbose is True

    @patch("winbins.cli.list_tools")
    def test_main_list_with_category(self, mock_list_tools):
        """Test main with --list and --category."""
        mock_list_tools.return_value = 0

        result = main(["--list", "--category", "enumeration"])

        assert result == 0
        mock_list_tools.assert_called_once()
        call_args = mock_list_tools.call_args
        assert call_args[0][1] == "enumeration"  # category argument


class TestCLIIntegration:
    """Integration tests for CLI."""

    @patch("sys.stdout", new_callable=StringIO)
    def test_list_tools_integration(self, mock_stdout):
        """Test listing tools end-to-end."""
        result = main(["--list"])

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Available Tools:" in output
        assert "Total:" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_search_integration(self, mock_stdout):
        """Test search end-to-end."""
        result = main(["--search", "kerberos"])

        assert result == 0
        output = mock_stdout.getvalue()
        assert "rubeus" in output

    @patch("winbins.builders.BuilderFactory.list_available")
    @patch("winbins.git_ops.GitOperations.is_git_available")
    @patch("sys.stdout", new_callable=StringIO)
    def test_check_deps_integration(self, mock_stdout, mock_git, mock_builders):
        """Test dependency check end-to-end."""
        mock_builders.return_value = {"msbuild": True, "dotnet": True}
        mock_git.return_value = True

        result = main(["--check-deps"])

        assert result == 0
        output = mock_stdout.getvalue()
        assert "Build Dependencies Status:" in output
