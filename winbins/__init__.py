"""
WinBins - Automated Windows Pentesting Binary Compiler
A modular framework for pulling and compiling the latest versions of popular pentesting tools.
"""

__version__ = "2.0.0"
__author__ = "WinBins Contributors"

from winbins.core import WinToolsUpdater
from winbins.tools.registry import ToolRegistry, TOOLS

__all__ = ["WinToolsUpdater", "ToolRegistry", "TOOLS"]
