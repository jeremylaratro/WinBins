#!/usr/bin/env python3
"""
WinTools Updater - Automated Windows Pentesting Binary Compiler
Pulls latest versions of popular pentesting tools and compiles them.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Tool definitions - easily extensible
TOOLS = {
    "rubeus": {
        "repo": "https://github.com/GhostPack/Rubeus.git",
        "build_cmd": ["msbuild", "Rubeus.sln", "/p:Configuration=Release"],
        "output": "Rubeus/bin/Release/Rubeus.exe",
        "requires": "msbuild"
    },
    "seatbelt": {
        "repo": "https://github.com/GhostPack/Seatbelt.git",
        "build_cmd": ["msbuild", "Seatbelt.sln", "/p:Configuration=Release"],
        "output": "Seatbelt/bin/Release/Seatbelt.exe",
        "requires": "msbuild"
    },
    "sharpup": {
        "repo": "https://github.com/GhostPack/SharpUp.git",
        "build_cmd": ["msbuild", "SharpUp.sln", "/p:Configuration=Release"],
        "output": "SharpUp/bin/Release/SharpUp.exe",
        "requires": "msbuild"
    },
    "sharphound": {
        "repo": "https://github.com/BloodHoundAD/SharpHound.git",
        "build_cmd": ["dotnet", "build", "-c", "Release"],
        "output": "src/bin/Release/net462/SharpHound.exe",
        "requires": "dotnet"
    },
    "certify": {
        "repo": "https://github.com/GhostPack/Certify.git",
        "build_cmd": ["msbuild", "Certify.sln", "/p:Configuration=Release"],
        "output": "Certify/bin/Release/Certify.exe",
        "requires": "msbuild"
    },
    "mimikatz": {
        "repo": "https://github.com/gentilkiwi/mimikatz.git",
        "build_cmd": ["msbuild", "mimikatz.sln", "/p:Configuration=Release", "/p:Platform=x64"],
        "output": "x64/Release/mimikatz.exe",
        "requires": "msbuild"
    },
    "inveigh": {
        "repo": "https://github.com/Kevin-Robertson/Inveigh.git",
        "build_cmd": ["dotnet", "build", "Inveigh.sln", "-c", "Release"],
        "output": "Inveigh/bin/Release/net462/Inveigh.exe",
        "requires": "dotnet"
    },
}


class WinToolsUpdater:
    def __init__(self, output_dir: str, build_dir: str, verbose: bool = False):
        self.output_dir = Path(output_dir)
        self.build_dir = Path(build_dir)
        self.verbose = verbose
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def log(self, msg: str, level: str = "INFO"):
        """Simple logging"""
        prefix = f"[{level}]"
        print(f"{prefix} {msg}")

    def run_cmd(self, cmd: List[str], cwd: Optional[Path] = None) -> bool:
        """Execute command and return success status"""
        try:
            if self.verbose:
                self.log(f"Running: {' '.join(cmd)}", "DEBUG")
            
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=not self.verbose,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {' '.join(cmd)}", "ERROR")
            if self.verbose and e.stderr:
                self.log(e.stderr, "ERROR")
            return False
        except FileNotFoundError:
            self.log(f"Command not found: {cmd[0]}", "ERROR")
            return False

    def check_dependencies(self, tool_name: str, tool_config: Dict) -> bool:
        """Check if build dependencies are available"""
        required = tool_config.get("requires")
        if not required:
            return True
        
        if shutil.which(required) is None:
            self.log(f"Missing dependency for {tool_name}: {required}", "ERROR")
            return False
        return True

    def clone_or_update(self, tool_name: str, repo_url: str, branch: Optional[str] = None) -> Optional[Path]:
        """Clone or update git repository"""
        tool_path = self.build_dir / tool_name
        
        if tool_path.exists():
            self.log(f"Updating {tool_name}...")
            if not self.run_cmd(["git", "-C", str(tool_path), "fetch", "--all"]):
                return None
            
            # Reset to latest
            target = f"origin/{branch}" if branch else "origin/HEAD"
            if not self.run_cmd(["git", "-C", str(tool_path), "reset", "--hard", target]):
                return None
            
            if not self.run_cmd(["git", "-C", str(tool_path), "clean", "-fdx"]):
                return None
        else:
            self.log(f"Cloning {tool_name}...")
            cmd = ["git", "clone", repo_url, str(tool_path)]
            if branch:
                cmd.extend(["-b", branch])
            
            if not self.run_cmd(cmd):
                return None
        
        return tool_path

    def build_tool(self, tool_name: str, tool_config: Dict, tool_path: Path) -> bool:
        """Build the tool from source"""
        self.log(f"Building {tool_name}...")
        
        build_cmd = tool_config["build_cmd"]
        if not self.run_cmd(build_cmd, cwd=tool_path):
            return False
        
        # Copy output to final location
        output_path = tool_path / tool_config["output"]
        if not output_path.exists():
            self.log(f"Build artifact not found: {output_path}", "ERROR")
            return False
        
        dest_path = self.output_dir / output_path.name
        shutil.copy2(output_path, dest_path)
        self.log(f"✓ {tool_name} -> {dest_path}", "SUCCESS")
        return True

    def update_tool(self, tool_name: str, branch: Optional[str] = None) -> bool:
        """Update and build a single tool"""
        if tool_name not in TOOLS:
            self.log(f"Unknown tool: {tool_name}", "ERROR")
            return False
        
        tool_config = TOOLS[tool_name]
        
        # Check dependencies
        if not self.check_dependencies(tool_name, tool_config):
            return False
        
        # Clone/update repository
        tool_path = self.clone_or_update(tool_name, tool_config["repo"], branch)
        if not tool_path:
            return False
        
        # Build
        return self.build_tool(tool_name, tool_config, tool_path)

    def update_all(self, branch: Optional[str] = None, tools: Optional[List[str]] = None) -> Dict[str, bool]:
        """Update specified tools or all tools"""
        tools_to_update = tools if tools else list(TOOLS.keys())
        results = {}
        
        for tool_name in tools_to_update:
            self.log(f"\n{'='*60}")
            self.log(f"Processing: {tool_name.upper()}")
            self.log(f"{'='*60}")
            
            success = self.update_tool(tool_name, branch)
            results[tool_name] = success
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Automated Windows Pentesting Binary Compiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available tools: {', '.join(TOOLS.keys())}

Examples:
  # Update all tools
  %(prog)s
  
  # Update specific tools
  %(prog)s -t rubeus certify sharphound
  
  # Update with specific branch
  %(prog)s -t rubeus -b dev
  
  # Custom output directory
  %(prog)s -o /opt/pentesting/windows-tools
        """
    )
    
    parser.add_argument(
        "-o", "--output",
        default="./binaries",
        help="Output directory for compiled binaries (default: ./binaries)"
    )
    
    parser.add_argument(
        "-b", "--build-dir",
        default="./build",
        help="Build directory for source code (default: ./build)"
    )
    
    parser.add_argument(
        "-t", "--tools",
        nargs="+",
        choices=list(TOOLS.keys()),
        help="Specific tools to update (default: all)"
    )
    
    parser.add_argument(
        "--branch",
        help="Git branch to use (default: default branch)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available tools and exit"
    )
    
    args = parser.parse_args()
    
    if args.list:
        print("\nAvailable Tools:")
        print("=" * 60)
        for name, config in TOOLS.items():
            print(f"\n{name}")
            print(f"  Repository: {config['repo']}")
            print(f"  Requires: {config.get('requires', 'N/A')}")
        return 0
    
    updater = WinToolsUpdater(args.output, args.build_dir, args.verbose)
    
    print("\n" + "=" * 60)
    print("Windows Pentesting Tools Updater")
    print("=" * 60)
    
    results = updater.update_all(args.branch, args.tools)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    for tool, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{tool:.<30} {status}")
    
    print(f"\nCompleted: {success_count}/{total_count}")
    print(f"Output directory: {updater.output_dir.absolute()}")
    
    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
