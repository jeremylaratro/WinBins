"""
Tests for the additional_tools module.
"""

import pytest
from winbins.tools.additional_tools import (
    ADDITIONAL_TOOLS,
    get_additional_tools,
    register_additional_tools,
)
from winbins.tools.registry import ToolRegistry


class TestAdditionalTools:
    """Tests for ADDITIONAL_TOOLS dictionary."""

    def test_additional_tools_not_empty(self):
        """Test that additional tools are defined."""
        assert len(ADDITIONAL_TOOLS) > 0

    def test_all_tools_have_required_fields(self):
        """Test that all additional tools have required fields."""
        required_fields = ["repo", "build_cmd", "output", "requires"]
        for name, config in ADDITIONAL_TOOLS.items():
            for field in required_fields:
                assert field in config, f"{name} missing '{field}'"

    def test_all_repos_are_valid_urls(self):
        """Test that all repos are valid GitHub URLs."""
        for name, config in ADDITIONAL_TOOLS.items():
            repo = config["repo"]
            assert repo.startswith("https://github.com/"), \
                f"{name} has invalid repo URL: {repo}"
            assert repo.endswith(".git"), \
                f"{name} repo should end with .git: {repo}"

    def test_all_build_cmds_are_lists(self):
        """Test that all build commands are lists."""
        for name, config in ADDITIONAL_TOOLS.items():
            assert isinstance(config["build_cmd"], list), \
                f"{name} build_cmd should be a list"
            assert len(config["build_cmd"]) > 0, \
                f"{name} build_cmd should not be empty"

    def test_categories_are_valid(self):
        """Test that all categories are valid."""
        valid_categories = {
            "credential_access", "enumeration", "privilege_escalation",
            "lateral_movement", "persistence", "collection", "evasion",
            "execution", "command_control", "network", "utility"
        }
        for name, config in ADDITIONAL_TOOLS.items():
            if "category" in config:
                assert config["category"] in valid_categories, \
                    f"{name} has invalid category: {config['category']}"

    def test_kerbrute_config(self):
        """Test kerbrute tool configuration."""
        assert "kerbrute" in ADDITIONAL_TOOLS
        config = ADDITIONAL_TOOLS["kerbrute"]
        assert "kerbrute" in config["repo"]
        assert config["requires"] == "go"
        assert "kerberos" in config["tags"]

    def test_whisker_config(self):
        """Test whisker tool configuration."""
        assert "whisker" in ADDITIONAL_TOOLS
        config = ADDITIONAL_TOOLS["whisker"]
        assert config["requires"] == "dotnet"
        assert config["category"] == "credential_access"

    def test_sweetpotato_config(self):
        """Test sweetpotato tool configuration."""
        assert "sweetpotato" in ADDITIONAL_TOOLS
        config = ADDITIONAL_TOOLS["sweetpotato"]
        assert config["category"] == "privilege_escalation"
        assert "privesc" in config["tags"]


class TestGetAdditionalTools:
    """Tests for get_additional_tools function."""

    def test_get_additional_tools_returns_copy(self):
        """Test that get_additional_tools returns a copy."""
        tools1 = get_additional_tools()
        tools2 = get_additional_tools()

        # Should be equal but not same object
        assert tools1 == tools2
        assert tools1 is not tools2

    def test_get_additional_tools_modification_safe(self):
        """Test that modifying returned dict doesn't affect original."""
        tools = get_additional_tools()
        tools["new_tool"] = {"repo": "test"}

        # Original should not be modified
        assert "new_tool" not in ADDITIONAL_TOOLS

    def test_get_additional_tools_contains_all_tools(self):
        """Test that returned dict contains all tools."""
        tools = get_additional_tools()
        assert len(tools) == len(ADDITIONAL_TOOLS)
        for name in ADDITIONAL_TOOLS:
            assert name in tools


class TestRegisterAdditionalTools:
    """Tests for register_additional_tools function."""

    def test_register_additional_tools_adds_all(self):
        """Test that all additional tools are registered."""
        registry = ToolRegistry(tools={})
        count = register_additional_tools(registry)

        assert count == len(ADDITIONAL_TOOLS)
        for name in ADDITIONAL_TOOLS:
            assert name in registry

    def test_register_additional_tools_to_existing_registry(self):
        """Test registering to registry with existing tools."""
        registry = ToolRegistry()  # Has default tools
        original_count = len(registry)

        count = register_additional_tools(registry)

        assert count == len(ADDITIONAL_TOOLS)
        assert len(registry) == original_count + len(ADDITIONAL_TOOLS)

    def test_register_additional_tools_tool_configs_valid(self):
        """Test that registered tools have valid configurations."""
        registry = ToolRegistry(tools={})
        register_additional_tools(registry)

        for name in ADDITIONAL_TOOLS:
            tool = registry.get(name)
            assert tool is not None
            assert tool.name == name
            assert tool.repo == ADDITIONAL_TOOLS[name]["repo"]

    def test_register_additional_tools_returns_count(self):
        """Test that function returns correct count."""
        registry = ToolRegistry(tools={})
        count = register_additional_tools(registry)

        assert isinstance(count, int)
        assert count > 0
        assert count == len(registry)
