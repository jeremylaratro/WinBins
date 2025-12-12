"""
Tests for the config module.
"""

import json
import pytest
from pathlib import Path

from winbins.config import Config, ConfigError, load_config


class TestConfig:
    """Tests for Config class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = Config()

        assert config.output_dir == "./binaries"
        assert config.build_dir == "./build"
        assert config.tools == {}
        assert config.enabled_tools is None

    def test_load_json_config(self, temp_dir):
        """Test loading JSON configuration."""
        config_data = {
            "output_dir": "/custom/output",
            "build_dir": "/custom/build",
            "tools": {
                "custom_tool": {
                    "repo": "https://github.com/test/tool.git",
                    "build_cmd": ["make"],
                    "output": "bin/tool",
                    "requires": "make"
                }
            }
        }

        config_path = temp_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        config = Config(str(config_path))

        assert config.output_dir == "/custom/output"
        assert config.build_dir == "/custom/build"
        assert "custom_tool" in config.tools

    def test_load_nonexistent_config(self, temp_dir):
        """Test loading non-existent config file."""
        config = Config(str(temp_dir / "nonexistent.json"))
        # Should not raise, just use defaults
        assert config.output_dir == "./binaries"

    def test_get_nested_value(self, temp_dir):
        """Test getting nested configuration values."""
        config_data = {
            "level1": {
                "level2": {
                    "value": "nested_value"
                }
            }
        }

        config_path = temp_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        config = Config(str(config_path))

        assert config.get("level1.level2.value") == "nested_value"

    def test_get_with_default(self):
        """Test getting value with default."""
        config = Config()

        result = config.get("nonexistent", "default_value")
        assert result == "default_value"

    def test_set_value(self):
        """Test setting configuration values."""
        config = Config()
        config.set("test.nested.value", "test_value")

        assert config.get("test.nested.value") == "test_value"

    def test_save_json_config(self, temp_dir):
        """Test saving configuration to JSON."""
        config = Config()
        config.set("output_dir", "/new/output")
        config.set("tools.new_tool.repo", "https://github.com/test/tool.git")

        save_path = temp_dir / "saved_config.json"
        config.save(str(save_path))

        # Verify saved file
        with open(save_path) as f:
            saved_data = json.load(f)

        assert saved_data["output_dir"] == "/new/output"
        assert "new_tool" in saved_data["tools"]

    def test_save_without_path_raises(self):
        """Test saving without path raises error."""
        config = Config()

        with pytest.raises(ConfigError):
            config.save()

    def test_unsupported_format_raises(self, temp_dir):
        """Test unsupported config format raises error."""
        config_path = temp_dir / "config.txt"
        config_path.touch()

        with pytest.raises(ConfigError):
            Config(str(config_path))


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_default(self):
        """Test load_config with no path."""
        config = load_config()
        assert isinstance(config, Config)

    def test_load_config_with_path(self, temp_dir):
        """Test load_config with path."""
        config_path = temp_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump({"output_dir": "/test"}, f)

        config = load_config(str(config_path))
        assert config.output_dir == "/test"
