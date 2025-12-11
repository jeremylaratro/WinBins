"""
Base tool definitions and interfaces for WinBins.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any


class BuildSystem(Enum):
    """Supported build systems."""
    MSBUILD = "msbuild"
    DOTNET = "dotnet"
    CMAKE = "cmake"
    MAKE = "make"
    CUSTOM = "custom"


class ToolCategory(Enum):
    """Tool categories for organization."""
    CREDENTIAL_ACCESS = "credential_access"
    ENUMERATION = "enumeration"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    LATERAL_MOVEMENT = "lateral_movement"
    PERSISTENCE = "persistence"
    COLLECTION = "collection"
    EVASION = "evasion"
    EXECUTION = "execution"
    COMMAND_CONTROL = "command_control"
    NETWORK = "network"
    UTILITY = "utility"


@dataclass
class ToolConfig:
    """Configuration for a pentesting tool."""

    name: str
    repo: str
    build_cmd: List[str]
    output: str
    requires: str
    build_system: BuildSystem = BuildSystem.MSBUILD
    description: str = ""
    category: ToolCategory = ToolCategory.UTILITY
    tags: List[str] = field(default_factory=list)
    pre_build_cmd: Optional[List[str]] = None
    post_build_cmd: Optional[List[str]] = None
    additional_outputs: List[str] = field(default_factory=list)
    env_vars: Dict[str, str] = field(default_factory=dict)
    platforms: List[str] = field(default_factory=lambda: ["windows"])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "repo": self.repo,
            "build_cmd": self.build_cmd,
            "output": self.output,
            "requires": self.requires,
            "build_system": self.build_system.value,
            "description": self.description,
            "category": self.category.value,
            "tags": self.tags,
            "pre_build_cmd": self.pre_build_cmd,
            "post_build_cmd": self.post_build_cmd,
            "additional_outputs": self.additional_outputs,
            "env_vars": self.env_vars,
            "platforms": self.platforms,
        }

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "ToolConfig":
        """Create ToolConfig from dictionary."""
        build_system = data.get("build_system", "msbuild")
        if isinstance(build_system, str):
            build_system = BuildSystem(build_system)

        category = data.get("category", "utility")
        if isinstance(category, str):
            category = ToolCategory(category)

        return cls(
            name=name,
            repo=data["repo"],
            build_cmd=data["build_cmd"],
            output=data["output"],
            requires=data.get("requires", ""),
            build_system=build_system,
            description=data.get("description", ""),
            category=category,
            tags=data.get("tags", []),
            pre_build_cmd=data.get("pre_build_cmd"),
            post_build_cmd=data.get("post_build_cmd"),
            additional_outputs=data.get("additional_outputs", []),
            env_vars=data.get("env_vars", {}),
            platforms=data.get("platforms", ["windows"]),
        )
