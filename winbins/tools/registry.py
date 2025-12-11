"""
Tool registry for WinBins.
Manages the collection of available pentesting tools.
"""

from typing import Any, Dict, Iterator, List, Optional
from winbins.tools.base import ToolConfig, ToolCategory, BuildSystem


# Default tool definitions
TOOLS: Dict[str, Dict[str, Any]] = {
    "rubeus": {
        "repo": "https://github.com/GhostPack/Rubeus.git",
        "build_cmd": ["msbuild", "Rubeus.sln", "/p:Configuration=Release"],
        "output": "Rubeus/bin/Release/Rubeus.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Kerberos interaction and abuse toolkit",
        "category": "credential_access",
        "tags": ["kerberos", "ad", "tickets"],
    },
    "seatbelt": {
        "repo": "https://github.com/GhostPack/Seatbelt.git",
        "build_cmd": ["msbuild", "Seatbelt.sln", "/p:Configuration=Release"],
        "output": "Seatbelt/bin/Release/Seatbelt.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Host-based enumeration and security checks",
        "category": "enumeration",
        "tags": ["enumeration", "recon", "host"],
    },
    "sharpup": {
        "repo": "https://github.com/GhostPack/SharpUp.git",
        "build_cmd": ["msbuild", "SharpUp.sln", "/p:Configuration=Release"],
        "output": "SharpUp/bin/Release/SharpUp.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Privilege escalation vulnerability checker",
        "category": "privilege_escalation",
        "tags": ["privesc", "enumeration"],
    },
    "sharphound": {
        "repo": "https://github.com/BloodHoundAD/SharpHound.git",
        "build_cmd": ["dotnet", "build", "-c", "Release"],
        "output": "src/bin/Release/net462/SharpHound.exe",
        "requires": "dotnet",
        "build_system": "dotnet",
        "description": "BloodHound data collector for AD enumeration",
        "category": "enumeration",
        "tags": ["bloodhound", "ad", "graph"],
    },
    "certify": {
        "repo": "https://github.com/GhostPack/Certify.git",
        "build_cmd": ["msbuild", "Certify.sln", "/p:Configuration=Release"],
        "output": "Certify/bin/Release/Certify.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "AD Certificate Services enumeration and abuse",
        "category": "credential_access",
        "tags": ["adcs", "certificates", "pki"],
    },
    "mimikatz": {
        "repo": "https://github.com/gentilkiwi/mimikatz.git",
        "build_cmd": ["msbuild", "mimikatz.sln", "/p:Configuration=Release", "/p:Platform=x64"],
        "output": "x64/Release/mimikatz.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Windows credential extraction toolkit",
        "category": "credential_access",
        "tags": ["credentials", "lsass", "dpapi"],
    },
    "inveigh": {
        "repo": "https://github.com/Kevin-Robertson/Inveigh.git",
        "build_cmd": ["dotnet", "build", "Inveigh.sln", "-c", "Release"],
        "output": "Inveigh/bin/Release/net462/Inveigh.exe",
        "requires": "dotnet",
        "build_system": "dotnet",
        "description": "LLMNR/NBNS/mDNS/DNS spoofer and relay tool",
        "category": "network",
        "tags": ["spoofing", "relay", "network"],
    },
}


class ToolRegistry:
    """
    Registry for managing pentesting tools.
    Allows easy addition, removal, and querying of tools.
    """

    def __init__(self, tools: Optional[Dict[str, Dict[str, Any]]] = None):
        """Initialize registry with optional custom tools."""
        self._tools: Dict[str, ToolConfig] = {}

        # Load default tools
        initial_tools = tools if tools is not None else TOOLS
        for name, config in initial_tools.items():
            self.register(name, config)

    def register(self, name: str, config: Dict[str, Any]) -> None:
        """Register a new tool."""
        self._tools[name] = ToolConfig.from_dict(name, config)

    def unregister(self, name: str) -> bool:
        """Remove a tool from the registry."""
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[ToolConfig]:
        """Get tool configuration by name."""
        return self._tools.get(name)

    def get_dict(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool configuration as dictionary (for backwards compatibility)."""
        tool = self._tools.get(name)
        return tool.to_dict() if tool else None

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def list_by_category(self, category: ToolCategory) -> List[str]:
        """List tools by category."""
        return [
            name for name, tool in self._tools.items()
            if tool.category == category
        ]

    def list_by_tag(self, tag: str) -> List[str]:
        """List tools that have a specific tag."""
        return [
            name for name, tool in self._tools.items()
            if tag in tool.tags
        ]

    def list_by_build_system(self, build_system: BuildSystem) -> List[str]:
        """List tools by build system."""
        return [
            name for name, tool in self._tools.items()
            if tool.build_system == build_system
        ]

    def search(self, query: str) -> List[str]:
        """Search tools by name, description, or tags."""
        query_lower = query.lower()
        results = []
        for name, tool in self._tools.items():
            if (query_lower in name.lower() or
                query_lower in tool.description.lower() or
                any(query_lower in tag.lower() for tag in tool.tags)):
                results.append(name)
        return results

    def __contains__(self, name: str) -> bool:
        """Check if tool is registered."""
        return name in self._tools

    def __len__(self) -> int:
        """Return number of registered tools."""
        return len(self._tools)

    def __iter__(self) -> Iterator[str]:
        """Iterate over tool names."""
        return iter(self._tools)

    def items(self) -> Iterator[tuple]:
        """Iterate over (name, ToolConfig) pairs."""
        for name, tool in self._tools.items():
            yield name, tool

    def merge(self, other: "ToolRegistry") -> None:
        """Merge another registry into this one."""
        for name, tool in other._tools.items():
            self._tools[name] = tool

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """Export registry as dictionary."""
        return {name: tool.to_dict() for name, tool in self._tools.items()}


# Default registry instance
_default_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get or create the default tool registry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = ToolRegistry()
    return _default_registry


def register_tool(name: str, config: Dict[str, Any]) -> None:
    """Register a tool in the default registry."""
    get_registry().register(name, config)
