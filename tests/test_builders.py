"""
Tests for the builders module.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from winbins.builders.base import Builder, BuildResult
from winbins.builders.msbuild import MSBuildBuilder
from winbins.builders.dotnet import DotNetBuilder
from winbins.builders.factory import BuilderFactory, get_builder
from winbins.tools.base import BuildSystem


class TestBuildResult:
    """Tests for BuildResult dataclass."""

    def test_success_result(self):
        """Test successful build result."""
        result = BuildResult(
            success=True,
            output_path=Path("/output/tool.exe"),
            return_code=0,
        )
        assert result.success is True
        assert result.failed is False
        assert result.output_path == Path("/output/tool.exe")

    def test_failed_result(self):
        """Test failed build result."""
        result = BuildResult(
            success=False,
            error_message="Build failed",
            return_code=1,
        )
        assert result.success is False
        assert result.failed is True
        assert result.error_message == "Build failed"

    def test_artifacts_list(self):
        """Test artifacts list in result."""
        result = BuildResult(
            success=True,
            artifacts=[Path("/a.exe"), Path("/b.dll")],
        )
        assert len(result.artifacts) == 2


class TestMSBuildBuilder:
    """Tests for MSBuildBuilder class."""

    def test_builder_properties(self):
        """Test builder properties."""
        builder = MSBuildBuilder()
        assert builder.name == "MSBuild"
        assert builder.executable == "msbuild"

    def test_custom_configuration(self):
        """Test custom configuration options."""
        builder = MSBuildBuilder(configuration="Debug", platform="x64")
        assert builder.configuration == "Debug"
        assert builder.platform == "x64"

    def test_default_build_cmd(self):
        """Test generating default build command."""
        builder = MSBuildBuilder(configuration="Release", platform="x64")
        cmd = builder.get_default_build_cmd("Project.sln")

        assert "msbuild" in cmd
        assert "Project.sln" in cmd
        assert "/p:Configuration=Release" in cmd
        assert "/p:Platform=x64" in cmd

    def test_default_build_cmd_no_platform(self):
        """Test build command without platform."""
        builder = MSBuildBuilder()
        cmd = builder.get_default_build_cmd("Project.sln")

        assert "/p:Platform=" not in " ".join(cmd)

    @patch("shutil.which")
    def test_is_available_true(self, mock_which):
        """Test availability when msbuild is installed."""
        mock_which.return_value = "/usr/bin/msbuild"
        builder = MSBuildBuilder()
        assert builder.is_available() is True

    @patch("shutil.which")
    def test_is_available_false(self, mock_which):
        """Test availability when msbuild is not installed."""
        mock_which.return_value = None
        builder = MSBuildBuilder()
        assert builder.is_available() is False

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run):
        """Test running command successfully."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Build succeeded",
            stderr="",
        )
        builder = MSBuildBuilder()
        result = builder.run_command(["msbuild", "test.sln"])

        assert result.success is True
        assert result.return_code == 0

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Test running command that fails."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: Build failed",
        )
        builder = MSBuildBuilder()
        result = builder.run_command(["msbuild", "test.sln"])

        assert result.success is False
        assert result.return_code == 1

    @patch("subprocess.run")
    def test_run_command_not_found(self, mock_run):
        """Test running command that doesn't exist."""
        mock_run.side_effect = FileNotFoundError()
        builder = MSBuildBuilder()
        result = builder.run_command(["nonexistent"])

        assert result.success is False
        assert "not found" in result.error_message.lower()


class TestDotNetBuilder:
    """Tests for DotNetBuilder class."""

    def test_builder_properties(self):
        """Test builder properties."""
        builder = DotNetBuilder()
        assert builder.name == "DotNet"
        assert builder.executable == "dotnet"

    def test_custom_options(self):
        """Test custom configuration options."""
        builder = DotNetBuilder(
            configuration="Debug",
            framework="net6.0",
            runtime="win-x64"
        )
        assert builder.configuration == "Debug"
        assert builder.framework == "net6.0"
        assert builder.runtime == "win-x64"

    def test_default_build_cmd(self):
        """Test generating default build command."""
        builder = DotNetBuilder(configuration="Release")
        cmd = builder.get_default_build_cmd("Project.csproj")

        assert "dotnet" in cmd
        assert "build" in cmd
        assert "Project.csproj" in cmd
        assert "-c" in cmd
        assert "Release" in cmd

    def test_default_publish_cmd(self):
        """Test generating default publish command."""
        builder = DotNetBuilder(configuration="Release")
        cmd = builder.get_default_build_cmd(publish=True)

        assert "dotnet" in cmd
        assert "publish" in cmd

    def test_publish_with_runtime(self):
        """Test publish command with runtime."""
        builder = DotNetBuilder(runtime="win-x64")
        cmd = builder.get_default_build_cmd(publish=True)

        assert "-r" in cmd
        assert "win-x64" in cmd

    @patch("shutil.which")
    def test_is_available(self, mock_which):
        """Test availability check."""
        mock_which.return_value = "/usr/bin/dotnet"
        builder = DotNetBuilder()
        assert builder.is_available() is True


class TestBuilderFactory:
    """Tests for BuilderFactory class."""

    def test_create_msbuild_builder(self):
        """Test creating MSBuild builder."""
        builder = BuilderFactory.create(BuildSystem.MSBUILD)
        assert isinstance(builder, MSBuildBuilder)

    def test_create_dotnet_builder(self):
        """Test creating DotNet builder."""
        builder = BuilderFactory.create(BuildSystem.DOTNET)
        assert isinstance(builder, DotNetBuilder)

    def test_create_unsupported_builder(self):
        """Test creating unsupported builder returns None."""
        builder = BuilderFactory.create(BuildSystem.CMAKE)
        assert builder is None

    def test_create_with_options(self):
        """Test creating builder with options."""
        builder = BuilderFactory.create(
            BuildSystem.MSBUILD,
            verbose=True,
            env_vars={"TEST": "value"}
        )
        assert builder.verbose is True
        assert builder.env_vars == {"TEST": "value"}

    def test_get_for_tool_msbuild(self):
        """Test getting builder for msbuild requirement."""
        builder = BuilderFactory.get_for_tool("msbuild")
        assert isinstance(builder, MSBuildBuilder)

    def test_get_for_tool_dotnet(self):
        """Test getting builder for dotnet requirement."""
        builder = BuilderFactory.get_for_tool("dotnet")
        assert isinstance(builder, DotNetBuilder)

    def test_get_for_tool_case_insensitive(self):
        """Test getting builder is case insensitive."""
        builder = BuilderFactory.get_for_tool("MSBUILD")
        assert isinstance(builder, MSBuildBuilder)

    def test_get_for_tool_unknown(self):
        """Test getting builder for unknown requirement."""
        builder = BuilderFactory.get_for_tool("unknown")
        assert builder is None

    @patch.object(MSBuildBuilder, "is_available", return_value=True)
    @patch.object(DotNetBuilder, "is_available", return_value=False)
    def test_list_available(self, mock_dotnet, mock_msbuild):
        """Test listing available builders."""
        available = BuilderFactory.list_available()
        assert available["msbuild"] is True
        assert available["dotnet"] is False

    def test_register_custom_builder(self):
        """Test registering custom builder."""
        class CustomBuilder(Builder):
            @property
            def name(self):
                return "Custom"

            @property
            def executable(self):
                return "custom"

            def build(self, source_path, build_cmd, output_path):
                return BuildResult(success=True)

        BuilderFactory.register(BuildSystem.CMAKE, CustomBuilder)
        builder = BuilderFactory.create(BuildSystem.CMAKE)
        assert isinstance(builder, CustomBuilder)


class TestGetBuilderFunction:
    """Tests for get_builder convenience function."""

    def test_get_builder_msbuild(self):
        """Test get_builder for msbuild."""
        builder = get_builder("msbuild")
        assert isinstance(builder, MSBuildBuilder)

    def test_get_builder_dotnet(self):
        """Test get_builder for dotnet."""
        builder = get_builder("dotnet")
        assert isinstance(builder, DotNetBuilder)

    def test_get_builder_with_options(self):
        """Test get_builder with options."""
        builder = get_builder("msbuild", verbose=True)
        assert builder.verbose is True
