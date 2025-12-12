"""
Command-line interface for WinBins.
"""

import argparse
import sys
from typing import List, Optional

from winbins import __version__
from winbins.core import WinToolsUpdater
from winbins.tools.registry import ToolRegistry, TOOLS
from winbins.tools.base import ToolCategory
from winbins.config import load_config


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="winbins",
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
  %(prog)s -t rubeus --branch dev

  # Custom output directory
  %(prog)s -o /opt/pentesting/windows-tools

  # List tools by category
  %(prog)s --list --category credential_access

  # Search for tools
  %(prog)s --search kerberos
        """
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
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

    parser.add_argument(
        "--category",
        choices=[c.value for c in ToolCategory],
        help="Filter tools by category (use with --list)"
    )

    parser.add_argument(
        "--search",
        help="Search tools by name, description, or tags"
    )

    parser.add_argument(
        "-c", "--config",
        help="Path to configuration file (YAML or JSON)"
    )

    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Check build dependencies and exit"
    )

    return parser


def list_tools(registry: ToolRegistry, category: Optional[str] = None,
               search: Optional[str] = None) -> int:
    """List available tools."""
    print("\nAvailable Tools:")
    print("=" * 70)

    if search:
        tool_names = registry.search(search)
        if not tool_names:
            print(f"No tools found matching '{search}'")
            return 1
    elif category:
        cat = ToolCategory(category)
        tool_names = registry.list_by_category(cat)
        if not tool_names:
            print(f"No tools found in category '{category}'")
            return 1
    else:
        tool_names = registry.list_tools()

    for name in sorted(tool_names):
        tool = registry.get(name)
        if tool:
            print(f"\n{name}")
            print(f"  Description: {tool.description or 'N/A'}")
            print(f"  Repository:  {tool.repo}")
            print(f"  Requires:    {tool.requires or 'N/A'}")
            print(f"  Category:    {tool.category.value}")
            if tool.tags:
                print(f"  Tags:        {', '.join(tool.tags)}")

    print(f"\nTotal: {len(tool_names)} tools")
    return 0


def check_dependencies(registry: ToolRegistry) -> int:
    """Check build dependencies."""
    from winbins.builders import BuilderFactory

    print("\nBuild Dependencies Status:")
    print("=" * 40)

    available = BuilderFactory.list_available()
    for builder, is_available in available.items():
        status = "AVAILABLE" if is_available else "MISSING"
        symbol = "+" if is_available else "-"
        print(f"  [{symbol}] {builder}: {status}")

    # Check git
    from winbins.git_ops import GitOperations
    git = GitOperations()
    git_available = git.is_git_available()
    symbol = "+" if git_available else "-"
    status = "AVAILABLE" if git_available else "MISSING"
    print(f"  [{symbol}] git: {status}")

    print()

    # Show which tools can be built
    print("Tool Availability:")
    print("=" * 40)

    can_build = 0
    cannot_build = 0

    for name in sorted(registry.list_tools()):
        tool = registry.get(name)
        if tool:
            req = tool.requires
            is_available = available.get(req, False) if req else True
            symbol = "+" if is_available else "-"
            status = "Ready" if is_available else f"Missing {req}"
            print(f"  [{symbol}] {name}: {status}")
            if is_available:
                can_build += 1
            else:
                cannot_build += 1

    print(f"\nCan build: {can_build}/{can_build + cannot_build} tools")

    return 0 if cannot_build == 0 else 1


def run_update(args: argparse.Namespace) -> int:
    """Run the tool update process."""
    # Load configuration if provided
    config = load_config(args.config) if args.config else None

    # Create registry (merge config tools if available)
    registry = ToolRegistry()
    if config and config.tools:
        for name, tool_config in config.tools.items():
            registry.register(name, tool_config)

    # Validate tool names if specified
    if args.tools:
        for tool in args.tools:
            if tool not in registry:
                print(f"[ERROR] Unknown tool: {tool}")
                print(f"Available tools: {', '.join(registry.list_tools())}")
                return 1

    # Create updater
    output_dir = config.output_dir if config else args.output
    build_dir = config.build_dir if config else args.build_dir

    updater = WinToolsUpdater(
        output_dir=output_dir,
        build_dir=build_dir,
        verbose=args.verbose,
        registry=registry,
    )

    print("\n" + "=" * 60)
    print("Windows Pentesting Tools Updater")
    print("=" * 60)

    # Run updates
    results = updater.update_all(args.branch, args.tools)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    for tool, success in sorted(results.items()):
        status = "+ SUCCESS" if success else "- FAILED"
        print(f"{tool:.<35} {status}")

    print(f"\nCompleted: {success_count}/{total_count}")
    print(f"Output directory: {updater.output_dir.absolute()}")

    return 0 if success_count == total_count else 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    registry = ToolRegistry()

    if args.list or args.search:
        return list_tools(registry, args.category, args.search)

    if args.check_deps:
        return check_dependencies(registry)

    return run_update(args)


if __name__ == "__main__":
    sys.exit(main())
