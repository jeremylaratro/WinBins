"""
Additional modern Windows security tools for WinBins.
These tools represent cutting-edge additions to the pentesting toolkit.

To use these tools, import and register them:
    from winbins.tools.additional_tools import ADDITIONAL_TOOLS
    from winbins.tools.registry import get_registry

    registry = get_registry()
    for name, config in ADDITIONAL_TOOLS.items():
        registry.register(name, config)
"""

from typing import Dict, Any


# Modern cutting-edge Windows security tools
ADDITIONAL_TOOLS: Dict[str, Dict[str, Any]] = {
    # === Credential Access & Kerberos ===
    "kerbrute": {
        "repo": "https://github.com/ropnop/kerbrute.git",
        "build_cmd": ["go", "build", "-ldflags", "-s -w", "-o", "kerbrute.exe", "."],
        "output": "kerbrute.exe",
        "requires": "go",
        "build_system": "custom",
        "description": "Fast Kerberos brute-force and enumeration tool",
        "category": "credential_access",
        "tags": ["kerberos", "bruteforce", "enumeration", "ad"],
    },
    "whisker": {
        "repo": "https://github.com/eladshamir/Whisker.git",
        "build_cmd": ["dotnet", "build", "-c", "Release"],
        "output": "Whisker/bin/Release/net462/Whisker.exe",
        "requires": "dotnet",
        "build_system": "dotnet",
        "description": "Shadow Credentials attack tool for AD",
        "category": "credential_access",
        "tags": ["shadow-credentials", "ad", "certificates"],
    },
    "koh": {
        "repo": "https://github.com/GhostPack/Koh.git",
        "build_cmd": ["msbuild", "Koh.sln", "/p:Configuration=Release"],
        "output": "Koh/bin/Release/Koh.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Token impersonation via logon session monitoring",
        "category": "credential_access",
        "tags": ["tokens", "impersonation", "logon"],
    },

    # === Enumeration & Reconnaissance ===
    "snaffler": {
        "repo": "https://github.com/SnaffCon/Snaffler.git",
        "build_cmd": ["dotnet", "build", "-c", "Release"],
        "output": "Snaffler/bin/Release/net462/Snaffler.exe",
        "requires": "dotnet",
        "build_system": "dotnet",
        "description": "Find interesting files and credentials in AD environments",
        "category": "enumeration",
        "tags": ["file-hunting", "credentials", "shares", "ad"],
    },
    "adrecon": {
        "repo": "https://github.com/adrecon/ADRecon.git",
        "build_cmd": ["powershell", "-Command", "Copy-Item", "ADRecon.ps1", "ADRecon.ps1"],
        "output": "ADRecon.ps1",
        "requires": "powershell",
        "build_system": "custom",
        "description": "Active Directory reconnaissance and enumeration",
        "category": "enumeration",
        "tags": ["ad", "reconnaissance", "powershell"],
    },
    "pingcastle": {
        "repo": "https://github.com/vletoux/pingcastle.git",
        "build_cmd": ["msbuild", "PingCastle.sln", "/p:Configuration=Release"],
        "output": "PingCastle/bin/Release/PingCastle.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "AD security assessment tool with risk scoring",
        "category": "enumeration",
        "tags": ["ad", "assessment", "security-audit"],
    },
    "sharpmapexec": {
        "repo": "https://github.com/cube0x0/SharpMapExec.git",
        "build_cmd": ["dotnet", "build", "-c", "Release"],
        "output": "SharpMapExec/bin/Release/net462/SharpMapExec.exe",
        "requires": "dotnet",
        "build_system": "dotnet",
        "description": "Swiss army knife for pentesting Windows/AD environments",
        "category": "enumeration",
        "tags": ["lateral-movement", "enumeration", "ad"],
    },

    # === Privilege Escalation ===
    "sweetpotato": {
        "repo": "https://github.com/CCob/SweetPotato.git",
        "build_cmd": ["msbuild", "SweetPotato.sln", "/p:Configuration=Release"],
        "output": "SweetPotato/bin/Release/SweetPotato.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Local privilege escalation via token impersonation",
        "category": "privilege_escalation",
        "tags": ["potato", "privesc", "tokens"],
    },
    "godpotato": {
        "repo": "https://github.com/BeichenDream/GodPotato.git",
        "build_cmd": ["msbuild", "GodPotato.sln", "/p:Configuration=Release"],
        "output": "GodPotato/bin/Release/GodPotato.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Modern potato exploit for local privilege escalation",
        "category": "privilege_escalation",
        "tags": ["potato", "privesc", "impersonate"],
    },
    "printspoofer": {
        "repo": "https://github.com/itm4n/PrintSpoofer.git",
        "build_cmd": ["msbuild", "PrintSpoofer.sln", "/p:Configuration=Release", "/p:Platform=x64"],
        "output": "x64/Release/PrintSpoofer.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Privilege escalation via print spooler abuse",
        "category": "privilege_escalation",
        "tags": ["spooler", "privesc", "impersonate"],
    },
    "efspotato": {
        "repo": "https://github.com/zcgonvh/EfsPotato.git",
        "build_cmd": ["msbuild", "EfsPotato.sln", "/p:Configuration=Release"],
        "output": "EfsPotato/bin/Release/EfsPotato.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Privilege escalation via EFS RPC abuse",
        "category": "privilege_escalation",
        "tags": ["efs", "privesc", "potato"],
    },

    # === Lateral Movement ===
    "sharpsccm": {
        "repo": "https://github.com/Mayyhem/SharpSCCM.git",
        "build_cmd": ["dotnet", "build", "-c", "Release"],
        "output": "SharpSCCM/bin/Release/net462/SharpSCCM.exe",
        "requires": "dotnet",
        "build_system": "dotnet",
        "description": "SCCM/MECM lateral movement and exploitation",
        "category": "lateral_movement",
        "tags": ["sccm", "mecm", "lateral-movement"],
    },
    "sharprdp": {
        "repo": "https://github.com/0xthirteen/SharpRDP.git",
        "build_cmd": ["msbuild", "SharpRDP.sln", "/p:Configuration=Release"],
        "output": "SharpRDP/bin/Release/SharpRDP.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Remote desktop protocol command execution",
        "category": "lateral_movement",
        "tags": ["rdp", "command-execution", "lateral-movement"],
    },
    "sharpwmi": {
        "repo": "https://github.com/GhostPack/SharpWMI.git",
        "build_cmd": ["msbuild", "SharpWMI.sln", "/p:Configuration=Release"],
        "output": "SharpWMI/bin/Release/SharpWMI.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "WMI-based lateral movement toolkit",
        "category": "lateral_movement",
        "tags": ["wmi", "lateral-movement", "execution"],
    },

    # === Evasion & Defense Bypass ===
    "scarecrow": {
        "repo": "https://github.com/optiv/ScareCrow.git",
        "build_cmd": ["go", "build", "-ldflags", "-s -w", "-o", "ScareCrow.exe", "."],
        "output": "ScareCrow.exe",
        "requires": "go",
        "build_system": "custom",
        "description": "Payload creation framework for EDR bypass",
        "category": "evasion",
        "tags": ["edr-bypass", "payload", "shellcode"],
    },
    "sharpblock": {
        "repo": "https://github.com/CCob/SharpBlock.git",
        "build_cmd": ["msbuild", "SharpBlock.sln", "/p:Configuration=Release"],
        "output": "SharpBlock/bin/Release/SharpBlock.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "EDR bypass via DLL blocking",
        "category": "evasion",
        "tags": ["edr-bypass", "dll-blocking", "evasion"],
    },
    "sharpunhooker": {
        "repo": "https://github.com/GetRektBoy724/SharpUnhooker.git",
        "build_cmd": ["msbuild", "SharpUnhooker.sln", "/p:Configuration=Release"],
        "output": "SharpUnhooker/bin/Release/SharpUnhooker.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Unhook EDR hooks in current process",
        "category": "evasion",
        "tags": ["edr-bypass", "unhooking", "evasion"],
    },

    # === Persistence ===
    "sharppersist": {
        "repo": "https://github.com/mandiant/SharPersist.git",
        "build_cmd": ["msbuild", "SharPersist.sln", "/p:Configuration=Release"],
        "output": "SharPersist/bin/Release/SharPersist.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Windows persistence toolkit",
        "category": "persistence",
        "tags": ["persistence", "backdoor", "registry"],
    },

    # === AD CS (Certificate Services) ===
    "certipy": {
        "repo": "https://github.com/ly4k/Certipy.git",
        "build_cmd": ["pip", "install", "-e", "."],
        "output": "certipy",
        "requires": "python",
        "build_system": "custom",
        "description": "AD CS enumeration and abuse (Python)",
        "category": "credential_access",
        "tags": ["adcs", "certificates", "esc1-esc8"],
    },
    "forganern": {
        "repo": "https://github.com/GhostPack/ForgeCert.git",
        "build_cmd": ["msbuild", "ForgeCert.sln", "/p:Configuration=Release"],
        "output": "ForgeCert/bin/Release/ForgeCert.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Forge AD CS certificates for persistence",
        "category": "persistence",
        "tags": ["adcs", "certificates", "golden-cert"],
    },
    "passtheccert": {
        "repo": "https://github.com/AlmondOffSec/PassTheCert.git",
        "build_cmd": ["dotnet", "build", "-c", "Release"],
        "output": "PassTheCert/bin/Release/net462/PassTheCert.exe",
        "requires": "dotnet",
        "build_system": "dotnet",
        "description": "Pass-the-Certificate attack implementation",
        "category": "credential_access",
        "tags": ["adcs", "certificates", "schannel"],
    },

    # === Coercion Attacks ===
    "petitpotam": {
        "repo": "https://github.com/topotam/PetitPotam.git",
        "build_cmd": ["python", "-m", "py_compile", "PetitPotam.py"],
        "output": "PetitPotam.py",
        "requires": "python",
        "build_system": "custom",
        "description": "NTLM relay via MS-EFSRPC abuse (Python)",
        "category": "network",
        "tags": ["coercion", "relay", "efs"],
    },
    "coercer": {
        "repo": "https://github.com/p0dalirius/Coercer.git",
        "build_cmd": ["pip", "install", "-e", "."],
        "output": "coercer",
        "requires": "python",
        "build_system": "custom",
        "description": "Multi-protocol coercion attack tool",
        "category": "network",
        "tags": ["coercion", "relay", "multi-protocol"],
    },

    # === DPAPI & Credential Extraction ===
    "sharpdpapi": {
        "repo": "https://github.com/GhostPack/SharpDPAPI.git",
        "build_cmd": ["msbuild", "SharpDPAPI.sln", "/p:Configuration=Release"],
        "output": "SharpDPAPI/bin/Release/SharpDPAPI.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "DPAPI credential extraction and manipulation",
        "category": "credential_access",
        "tags": ["dpapi", "credentials", "masterkey"],
    },
    "sharpchrome": {
        "repo": "https://github.com/GhostPack/SharpDPAPI.git",
        "build_cmd": ["msbuild", "SharpChrome/SharpChrome.csproj", "/p:Configuration=Release"],
        "output": "SharpChrome/bin/Release/SharpChrome.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "Chrome credential extraction via DPAPI",
        "category": "credential_access",
        "tags": ["dpapi", "chrome", "browser", "credentials"],
    },

    # === Process Injection & Execution ===
    "donut": {
        "repo": "https://github.com/TheWover/donut.git",
        "build_cmd": ["make", "-f", "Makefile.msvc"],
        "output": "donut.exe",
        "requires": "make",
        "build_system": "make",
        "description": "Shellcode generator for .NET assemblies",
        "category": "execution",
        "tags": ["shellcode", "loader", "dotnet"],
    },
    "sharpview": {
        "repo": "https://github.com/tevora-threat/SharpView.git",
        "build_cmd": ["msbuild", "SharpView.sln", "/p:Configuration=Release"],
        "output": "SharpView/bin/Release/SharpView.exe",
        "requires": "msbuild",
        "build_system": "msbuild",
        "description": "C# implementation of PowerView",
        "category": "enumeration",
        "tags": ["ad", "enumeration", "powerview"],
    },
}


def get_additional_tools() -> Dict[str, Dict[str, Any]]:
    """Get all additional tool definitions."""
    return ADDITIONAL_TOOLS.copy()


def register_additional_tools(registry) -> int:
    """
    Register all additional tools in the given registry.

    Args:
        registry: ToolRegistry instance to register tools in

    Returns:
        Number of tools registered
    """
    count = 0
    for name, config in ADDITIONAL_TOOLS.items():
        registry.register(name, config)
        count += 1
    return count
