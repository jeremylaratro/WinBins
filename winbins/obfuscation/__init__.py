"""
Obfuscation utilities for WinBins.
Provides automated obfuscation capabilities for compiled binaries and source code.
"""

from winbins.obfuscation.base import (
    Obfuscator,
    ObfuscationResult,
    ObfuscationConfig,
)

__all__ = ["Obfuscator", "ObfuscationResult", "ObfuscationConfig"]
