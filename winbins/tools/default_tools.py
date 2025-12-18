"""
Default WinBins tool catalog.

Quick add template (copy/paste into DEFAULT_TOOLS):
    "tool_name": {
        "repo": "https://github.com/org/repo.git",
        "build_cmd": ["dotnet", "build", "-c", "Release"],
        "output": "path/to/output.exe",
        "requires": "dotnet",         # dotnet|msbuild|go|powershell|custom
        "build_system": "dotnet",     # matches requires or custom
        "description": "One-line summary of what this tool does",
        "category": "enumeration",    # see ToolCategory for options
        "tags": ["tag1", "tag2"],
    }
"""

from typing import Any, Dict

# Default tool definitions
DEFAULT_TOOLS: Dict[str, Dict[str, Any]] = {
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
