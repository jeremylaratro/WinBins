"""
Pytest configuration and fixtures for WinBins tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import MagicMock, patch


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def output_dir(temp_dir):
    """Create a temporary output directory."""
    output = temp_dir / "binaries"
    output.mkdir()
    return output


@pytest.fixture
def build_dir(temp_dir):
    """Create a temporary build directory."""
    build = temp_dir / "build"
    build.mkdir()
    return build


@pytest.fixture
def sample_tool_config() -> Dict[str, Any]:
    """Return a sample tool configuration."""
    return {
        "repo": "https://github.com/example/tool.git",
        "build_cmd": ["msbuild", "Tool.sln", "/p:Configuration=Release"],
        "output": "bin/Release/Tool.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "A sample tool for testing",
        "category": "utility",
        "tags": ["test", "sample"],
    }


@pytest.fixture
def sample_tools() -> Dict[str, Dict[str, Any]]:
    """Return a set of sample tool configurations."""
    return {
        "tool1": {
            "repo": "https://github.com/example/tool1.git",
            "build_cmd": ["msbuild", "Tool1.sln", "/p:Configuration=Release"],
            "output": "bin/Release/Tool1.exe",
            "requires": "msbuild",
        },
        "tool2": {
            "repo": "https://github.com/example/tool2.git",
            "build_cmd": ["dotnet", "build", "-c", "Release"],
            "output": "bin/Release/net6.0/Tool2.exe",
            "requires": "dotnet",
        },
    }


@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for command execution tests."""
    with patch("subprocess.run") as mock:
        mock.return_value = MagicMock(
            returncode=0,
            stdout="Success",
            stderr="",
        )
        yield mock


@pytest.fixture
def mock_shutil_which():
    """Mock shutil.which for dependency checking tests."""
    with patch("shutil.which") as mock:
        mock.return_value = "/usr/bin/mock"
        yield mock


@pytest.fixture
def mock_git_available(mock_subprocess):
    """Mock git as available."""
    mock_subprocess.return_value = MagicMock(
        returncode=0,
        stdout="git version 2.40.0",
        stderr="",
    )
    return mock_subprocess
