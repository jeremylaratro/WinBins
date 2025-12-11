"""
Configuration management for WinBins.
Supports loading tool configurations from YAML/JSON files.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try to import yaml, but make it optional
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigError(Exception):
    """Configuration error."""
    pass


class Config:
    """Configuration manager for WinBins."""

    DEFAULT_OUTPUT_DIR = "./binaries"
    DEFAULT_BUILD_DIR = "./build"

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else None
        self._data: Dict[str, Any] = {}

        if self.config_path:
            self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if not self.config_path or not self.config_path.exists():
            return

        suffix = self.config_path.suffix.lower()

        if suffix in ('.yml', '.yaml'):
            if not YAML_AVAILABLE:
                raise ConfigError("PyYAML not installed. Install with: pip install pyyaml")
            with open(self.config_path) as f:
                self._data = yaml.safe_load(f) or {}
        elif suffix == '.json':
            with open(self.config_path) as f:
                self._data = json.load(f)
        else:
            raise ConfigError(f"Unsupported config format: {suffix}")

    def save(self, path: Optional[str] = None) -> None:
        """Save configuration to file."""
        save_path = Path(path) if path else self.config_path
        if not save_path:
            raise ConfigError("No path specified for saving config")

        suffix = save_path.suffix.lower()

        if suffix in ('.yml', '.yaml'):
            if not YAML_AVAILABLE:
                raise ConfigError("PyYAML not installed. Install with: pip install pyyaml")
            with open(save_path, 'w') as f:
                yaml.dump(self._data, f, default_flow_style=False)
        elif suffix == '.json':
            with open(save_path, 'w') as f:
                json.dump(self._data, f, indent=2)
        else:
            raise ConfigError(f"Unsupported config format: {suffix}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self._data
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        keys = key.split('.')
        data = self._data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value

    @property
    def output_dir(self) -> str:
        """Get output directory."""
        return self.get('output_dir', self.DEFAULT_OUTPUT_DIR)

    @property
    def build_dir(self) -> str:
        """Get build directory."""
        return self.get('build_dir', self.DEFAULT_BUILD_DIR)

    @property
    def tools(self) -> Dict[str, Any]:
        """Get custom tool definitions."""
        return self.get('tools', {})

    @property
    def enabled_tools(self) -> Optional[List[str]]:
        """Get list of enabled tools."""
        return self.get('enabled_tools')


def load_config(path: Optional[str] = None) -> Config:
    """Load configuration from file or return default config."""
    return Config(path)
