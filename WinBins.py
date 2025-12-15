#!/usr/bin/env python3
import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple, List

TOOLS: Dict[str, Dict] = {
    "rubeus": {
        "repo": "https://github.com/GhostPack/Rubeus.git",
        "sln": "Rubeus.sln",
        "build": ["dotnet", "msbuild", "Rubeus.sln", "/p:Configuration=Release"],
        "exe": "Rubeus.exe",
        "netfx": True,
    },
    "seatbelt": {
        "repo": "https://github.com/GhostPack/Seatbelt.git",
        "sln": "Seatbelt.sln",
        "build": ["dotnet", "msbuild", "Seatbelt.sln", "/p:Configuration=Release"],
        "exe": "Seatbelt.exe",
        "netfx": True,
    },
    "sharpup": {
        "repo": "https://github.com/GhostPack/SharpUp.git",
        "sln": "SharpUp.sln",
        "build": ["dotnet", "msbuild", "SharpUp.sln", "/p:Configuration=Release"],
        "exe": "SharpUp.exe",
        "netfx": True,
    },
    "certify": {
        "repo": "https://github.com/GhostPack/Certify.git",
        "sln": "Certify.sln",
        # NOTE: we will override this in code to use the *absolute* sln path, per your working command
        "build": ["dotnet", "msbuild", "Certify.sln", "/p:Configuration=Release"],
        "exe": "Certify.exe",
        "netfx": True,
        "certify_special": True,  # use: nuget restore <abs sln> then dotnet msbuild <abs sln>
    },
    "sharphound": {
        "repo": "https://github.com/BloodHoundAD/SharpHound.git",
        "sln": None,
        "build": ["dotnet", "build", "-c", "Release"],
        "exe": "SharpHound.exe",
        "netfx": False,
    },
    "inveigh": {
        "repo": "https://github.com/Kevin-Robertson/Inveigh.git",
        "sln": None,
        "build": ["dotnet", "build", "-c", "Release"],
        "exe": "Inveigh.exe",
        "netfx": False,
    },
    "mimikatz": {
        "repo": "https://github.com/gentilkiwi/mimikatz.git",
        "skip_non_windows": True,
    },
}

NETFX_PROPS = """<Project>
  <ItemGroup>
    <PackageReference Include="Microsoft.NETFramework.ReferenceAssemblies"
                      Version="1.0.3"
                      PrivateAssets="All" />
  </ItemGroup>
</Project>
"""

class WinToolsUpdater:
    def __init__(self, output_dir: Path, build_dir: Path, verbose: bool = False):
        self.output_dir = output_dir.resolve()
        self.build_dir = build_dir.resolve()
        self.verbose = verbose
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def log(self, msg: str, level: str = "INFO"):
        print(f"[{level}] {msg}")

    def run_cmd(self, cmd: List[str], cwd: Optional[Path] = None) -> Tuple[bool, str]:
        try:
            if self.verbose:
                self.log(f"CMD: {' '.join(cmd)} (cwd={cwd})", "DEBUG")
                r = subprocess.run(cmd, cwd=cwd, text=True)
                return (r.returncode == 0), ""
            r = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
            return True, (r.stdout or "") + (r.stderr or "")
        except subprocess.CalledProcessError as e:
            out = ""
            if e.stdout: out += e.stdout
            if e.stderr: out += e.stderr
            return False, out
        except FileNotFoundError:
            return False, f"Command not found: {cmd[0]}"

    def clone_or_update(self, name: str, repo: str) -> Optional[Path]:
        dst = self.build_dir / name
        if dst.exists():
            self.log(f"Updating {name}...")
            ok, out = self.run_cmd(["git", "-C", str(dst), "fetch", "--all"])
            if not ok: self.log(out.strip() or "git fetch failed", "ERROR"); return None
            ok, out = self.run_cmd(["git", "-C", str(dst), "reset", "--hard", "origin/HEAD"])
            if not ok: self.log(out.strip() or "git reset failed", "ERROR"); return None
            ok, out = self.run_cmd(["git", "-C", str(dst), "clean", "-fdx"])
            if not ok: self.log(out.strip() or "git clean failed", "ERROR"); return None
        else:
            self.log(f"Cloning {name}...")
            ok, out = self.run_cmd(["git", "clone", repo, str(dst)])
            if not ok: self.log(out.strip() or "git clone failed", "ERROR"); return None
        return dst

    def ensure_netfx_reference_assemblies(self, tool_path: Path):
        props = tool_path / "Directory.Build.props"
        if not props.exists():
            props.write_text(NETFX_PROPS, encoding="utf-8")
            self.log("Injected .NET Framework reference assemblies (Directory.Build.props).")

    def restore_dotnet(self, tool_path: Path, sln_abs: Optional[Path] = None) -> bool:
        # For NETFX reference assemblies package, restoring the solution is safest.
        cmd = ["dotnet", "restore", str(sln_abs)] if sln_abs else ["dotnet", "restore"]
        self.log(f"Running {' '.join(cmd)}...")
        ok, out = self.run_cmd(cmd, cwd=tool_path)
        if not ok:
            self.log("\n".join(out.strip().splitlines()[-30:]) or "dotnet restore failed", "ERROR")
            return False
        return True

    def restore_certify_with_nuget(self, sln_abs: Path, cwd: Path) -> bool:
        if shutil.which("nuget") is None:
            self.log("Certify requires classic NuGet restore but 'nuget' is not in PATH. Install it: sudo dnf install nuget", "ERROR")
            return False
        self.log(f"Running nuget restore {sln_abs} ...")
        ok, out = self.run_cmd(["nuget", "restore", str(sln_abs)], cwd=cwd)
        if not ok:
            self.log("\n".join(out.strip().splitlines()[-30:]) or "nuget restore failed", "ERROR")
            return False
        return True

    def find_artifact(self, tool_path: Path, exe_name: str) -> Optional[Path]:
        matches = list(tool_path.rglob(exe_name))
        if not matches:
            return None
        matches.sort(key=lambda p: ("release" not in str(p).lower(), len(str(p))))
        return matches[0]

    def build_and_copy(self, name: str, cfg: Dict, tool_path: Path) -> bool:
        sln_rel = cfg.get("sln")
        sln_abs = (tool_path / sln_rel).resolve() if sln_rel else None

        # --- CERTIFY SPECIAL CASE (exact working sequence you provided) ---
        if cfg.get("certify_special"):
            if not sln_abs or not sln_abs.exists():
                self.log("Certify.sln not found", "ERROR")
                return False

            # 1) nuget restore <abs sln>  (gets dnMerge + packages folder layout)
            if not self.restore_certify_with_nuget(sln_abs, cwd=tool_path):
                return False

            # 2) dotnet restore <abs sln> (ensures Microsoft.NETFramework.ReferenceAssemblies is restored)
            if not self.restore_dotnet(tool_path, sln_abs=sln_abs):
                return False

            # 3) dotnet msbuild <abs sln> /p:Configuration=Release
            self.log(f"Building {name} (dotnet msbuild {sln_abs})...")
            ok, out = self.run_cmd(["dotnet", "msbuild", str(sln_abs), "/p:Configuration=Release"], cwd=tool_path)
            if not ok:
                self.log("\n".join(out.strip().splitlines()[-40:]) or "Build failed", "ERROR")
                return False
        else:
            # Normal flow for others
            if cfg.get("netfx"):
                # Restore solution if present; otherwise restore repo
                if sln_abs and sln_abs.exists():
                    if not self.restore_dotnet(tool_path, sln_abs=sln_abs):
                        return False
                else:
                    if not self.restore_dotnet(tool_path):
                        return False
            else:
                if not self.restore_dotnet(tool_path, sln_abs=sln_abs if sln_abs and sln_abs.exists() else None):
                    return False

            self.log(f"Building {name}...")
            ok, out = self.run_cmd(cfg["build"], cwd=tool_path)
            if not ok:
                self.log("\n".join(out.strip().splitlines()[-40:]) or "Build failed", "ERROR")
                return False

        exe_name = cfg["exe"]
        artifact = self.find_artifact(tool_path, exe_name)
        if not artifact or not artifact.exists():
            self.log(f"Build artifact not found: {exe_name}", "ERROR")
            return False

        dest = self.output_dir / artifact.name
        shutil.copy2(artifact, dest)
        self.log(f"✓ {name} -> {dest}", "SUCCESS")
        return True

    def update_tool(self, name: str) -> bool:
        cfg = TOOLS[name]

        if cfg.get("skip_non_windows") and platform.system() != "Windows":
            self.log(f"{name} is Windows-only, skipping", "INFO")
            return False

        tool_path = self.clone_or_update(name, cfg["repo"])
        if tool_path is None:
            return False

        if cfg.get("netfx"):
            self.ensure_netfx_reference_assemblies(tool_path)

        if "build" not in cfg:
            self.log(f"No build config for {name}", "ERROR")
            return False

        return self.build_and_copy(name, cfg, tool_path)

def main():
    parser = argparse.ArgumentParser(description="Windows Pentesting Tools Updater")
    parser.add_argument("-o", "--output", default="./binaries", help="Output directory (default: ./binaries)")
    parser.add_argument("-b", "--build-dir", default="./build", help="Build directory (default: ./build)")
    parser.add_argument("-t", "--tools", nargs="+", choices=list(TOOLS.keys()), help="Tools to build (default: all)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose command output")
    args = parser.parse_args()

    updater = WinToolsUpdater(Path(args.output), Path(args.build_dir), verbose=args.verbose)

    print("\n" + "=" * 60)
    print("Windows Pentesting Tools Updater")
    print("=" * 60)

    targets = args.tools if args.tools else list(TOOLS.keys())
    results: Dict[str, bool] = {}

    for name in targets:
        print("\n" + "=" * 60)
        updater.log(f"Processing: {name.upper()}")
        print("=" * 60)
        results[name] = updater.update_tool(name)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for k, v in results.items():
        print(f"{k:.<30} {'✓ SUCCESS' if v else '✗ FAILED'}")

    success = sum(1 for v in results.values() if v)
    print(f"\nCompleted: {success}/{len(results)}")
    print(f"Output directory: {updater.output_dir}")

    return 0 if success == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
