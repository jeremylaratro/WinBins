"""
Tests for the tools module.
"""

import pytest
from winbins.tools.base import (
    ToolConfig,
    ToolCategory,
    BuildSystem,
)
from winbins.tools.registry import (
    ToolRegistry,
    TOOLS,
    get_registry,
    register_tool,
)


class TestToolConfig:
    """Tests for ToolConfig dataclass."""

    def test_create_from_dict(self, sample_tool_config):
        """Test creating ToolConfig from dictionary."""
        config = ToolConfig.from_dict("test_tool", sample_tool_config)

        assert config.name == "test_tool"
        assert config.repo == sample_tool_config["repo"]
        assert config.build_cmd == sample_tool_config["build_cmd"]
        assert config.output == sample_tool_config["output"]
        assert config.requires == sample_tool_config["requires"]
        assert config.build_system == BuildSystem.MSBUILD
        assert config.category == ToolCategory.UTILITY

    def test_to_dict(self, sample_tool_config):
        """Test converting ToolConfig to dictionary."""
        config = ToolConfig.from_dict("test_tool", sample_tool_config)
        result = config.to_dict()

        assert result["name"] == "test_tool"
        assert result["repo"] == sample_tool_config["repo"]
        assert result["build_system"] == "msbuild"
        assert result["category"] == "utility"

    def test_default_values(self):
        """Test default values in ToolConfig."""
        config = ToolConfig(
            name="minimal",
            repo="https://github.com/test/test.git",
            build_cmd=["make"],
            output="bin/test",
            requires="make",
        )

        assert config.build_system == BuildSystem.MSBUILD
        assert config.category == ToolCategory.UTILITY
        assert config.tags == []
        assert config.platforms == ["windows"]

    def test_tool_categories(self):
        """Test all tool categories exist."""
        expected_categories = [
            "credential_access",
            "enumeration",
            "privilege_escalation",
            "lateral_movement",
            "persistence",
            "collection",
            "evasion",
            "execution",
            "command_control",
            "network",
            "utility",
        ]
        for cat in expected_categories:
            assert ToolCategory(cat) is not None

    def test_build_systems(self):
        """Test all build systems exist."""
        expected_systems = ["msbuild", "dotnet", "cmake", "make", "custom"]
        for system in expected_systems:
            assert BuildSystem(system) is not None


class TestToolRegistry:
    """Tests for ToolRegistry class."""

    def test_default_registry_has_tools(self):
        """Test that default registry contains predefined tools."""
        registry = ToolRegistry()
        assert len(registry) > 0
        assert "rubeus" in registry
        assert "mimikatz" in registry

    def test_empty_registry(self):
        """Test creating empty registry."""
        registry = ToolRegistry(tools={})
        assert len(registry) == 0

    def test_custom_registry(self, sample_tools):
        """Test creating registry with custom tools."""
        registry = ToolRegistry(tools=sample_tools)
        assert len(registry) == 2
        assert "tool1" in registry
        assert "tool2" in registry

    def test_register_tool(self, sample_tool_config):
        """Test registering a new tool."""
        registry = ToolRegistry(tools={})
        registry.register("new_tool", sample_tool_config)

        assert "new_tool" in registry
        tool = registry.get("new_tool")
        assert tool.repo == sample_tool_config["repo"]

    def test_unregister_tool(self, sample_tools):
        """Test removing a tool from registry."""
        registry = ToolRegistry(tools=sample_tools)
        assert "tool1" in registry

        result = registry.unregister("tool1")
        assert result is True
        assert "tool1" not in registry

    def test_unregister_nonexistent(self):
        """Test removing non-existent tool returns False."""
        registry = ToolRegistry(tools={})
        result = registry.unregister("nonexistent")
        assert result is False

    def test_get_tool(self):
        """Test getting a tool by name."""
        registry = ToolRegistry()
        tool = registry.get("rubeus")

        assert tool is not None
        assert tool.name == "rubeus"
        assert "GhostPack/Rubeus" in tool.repo

    def test_get_nonexistent(self):
        """Test getting non-existent tool returns None."""
        registry = ToolRegistry()
        assert registry.get("nonexistent") is None

    def test_get_dict(self):
        """Test getting tool as dictionary."""
        registry = ToolRegistry()
        tool_dict = registry.get_dict("rubeus")

        assert tool_dict is not None
        assert isinstance(tool_dict, dict)
        assert "repo" in tool_dict
        assert "build_cmd" in tool_dict

    def test_list_tools(self):
        """Test listing all tool names."""
        registry = ToolRegistry()
        tools = registry.list_tools()

        assert isinstance(tools, list)
        assert "rubeus" in tools
        assert "seatbelt" in tools

    def test_list_by_category(self):
        """Test listing tools by category."""
        registry = ToolRegistry()
        cred_tools = registry.list_by_category(ToolCategory.CREDENTIAL_ACCESS)

        assert isinstance(cred_tools, list)
        assert "rubeus" in cred_tools
        assert "mimikatz" in cred_tools

    def test_list_by_tag(self):
        """Test listing tools by tag."""
        registry = ToolRegistry()
        kerberos_tools = registry.list_by_tag("kerberos")

        assert isinstance(kerberos_tools, list)
        assert "rubeus" in kerberos_tools

    def test_list_by_build_system(self):
        """Test listing tools by build system."""
        registry = ToolRegistry()
        msbuild_tools = registry.list_by_build_system(BuildSystem.MSBUILD)
        dotnet_tools = registry.list_by_build_system(BuildSystem.DOTNET)

        assert "rubeus" in msbuild_tools
        assert "sharphound" in dotnet_tools

    def test_search(self):
        """Test searching tools."""
        registry = ToolRegistry()

        # Search by name
        results = registry.search("rubeus")
        assert "rubeus" in results

        # Search by description
        results = registry.search("kerberos")
        assert "rubeus" in results

        # Search by tag
        results = registry.search("ad")
        assert len(results) > 0

    def test_iteration(self):
        """Test iterating over registry."""
        registry = ToolRegistry()
        count = 0
        for name in registry:
            assert isinstance(name, str)
            count += 1
        assert count == len(registry)

    def test_items_iteration(self):
        """Test iterating over registry items."""
        registry = ToolRegistry()
        for name, tool in registry.items():
            assert isinstance(name, str)
            assert isinstance(tool, ToolConfig)
            assert tool.name == name

    def test_merge_registries(self, sample_tools):
        """Test merging two registries."""
        registry1 = ToolRegistry()
        original_count = len(registry1)

        registry2 = ToolRegistry(tools=sample_tools)
        registry1.merge(registry2)

        assert len(registry1) == original_count + 2
        assert "tool1" in registry1
        assert "tool2" in registry1

    def test_to_dict(self):
        """Test exporting registry as dictionary."""
        registry = ToolRegistry()
        result = registry.to_dict()

        assert isinstance(result, dict)
        for name, config in result.items():
            assert isinstance(config, dict)
            assert "repo" in config


class TestGlobalRegistry:
    """Tests for global registry functions."""

    def test_get_registry(self):
        """Test getting default registry."""
        registry = get_registry()
        assert registry is not None
        assert len(registry) > 0

    def test_register_tool_global(self, sample_tool_config):
        """Test registering tool in global registry."""
        register_tool("global_test_tool", sample_tool_config)
        registry = get_registry()
        assert "global_test_tool" in registry


class TestDefaultTools:
    """Tests for default tool definitions."""

    def test_all_tools_have_required_fields(self):
        """Test that all default tools have required fields."""
        for name, config in TOOLS.items():
            assert "repo" in config, f"{name} missing 'repo'"
            assert "build_cmd" in config, f"{name} missing 'build_cmd'"
            assert "output" in config, f"{name} missing 'output'"
            assert "requires" in config, f"{name} missing 'requires'"

    def test_all_repos_are_valid_urls(self):
        """Test that all repos are valid GitHub URLs."""
        for name, config in TOOLS.items():
            repo = config["repo"]
            assert repo.startswith("https://github.com/"), \
                f"{name} has invalid repo URL: {repo}"
            assert repo.endswith(".git"), \
                f"{name} repo should end with .git: {repo}"

    def test_all_build_cmds_are_lists(self):
        """Test that all build commands are lists."""
        for name, config in TOOLS.items():
            assert isinstance(config["build_cmd"], list), \
                f"{name} build_cmd should be a list"
            assert len(config["build_cmd"]) > 0, \
                f"{name} build_cmd should not be empty"

    def test_all_requires_are_valid(self):
        """Test that all requirements are valid build systems."""
        valid_requires = {"msbuild", "dotnet", "cmake", "make"}
        for name, config in TOOLS.items():
            req = config["requires"]
            assert req in valid_requires, \
                f"{name} has invalid requires: {req}"
