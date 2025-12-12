"""
Builder factory for WinBins.
Creates appropriate builder instances based on tool configuration.
"""

from typing import Dict, Optional, Type

from winbins.builders.base import Builder
from winbins.builders.msbuild import MSBuildBuilder
from winbins.builders.dotnet import DotNetBuilder
from winbins.tools.base import BuildSystem


class BuilderFactory:
    """
    Factory for creating builder instances.
    Allows registration of custom builders.
    """

    _builders: Dict[BuildSystem, Type[Builder]] = {
        BuildSystem.MSBUILD: MSBuildBuilder,
        BuildSystem.DOTNET: DotNetBuilder,
    }

    @classmethod
    def register(cls, build_system: BuildSystem, builder_class: Type[Builder]) -> None:
        """Register a custom builder class for a build system."""
        cls._builders[build_system] = builder_class

    @classmethod
    def create(cls, build_system: BuildSystem, verbose: bool = False,
               env_vars: Optional[Dict[str, str]] = None, **kwargs) -> Optional[Builder]:
        """
        Create a builder instance for the specified build system.

        Args:
            build_system: The build system type
            verbose: Enable verbose output
            env_vars: Environment variables to set during build
            **kwargs: Additional builder-specific arguments

        Returns:
            Builder instance or None if not supported
        """
        builder_class = cls._builders.get(build_system)
        if builder_class is None:
            return None

        return builder_class(verbose=verbose, env_vars=env_vars, **kwargs)

    @classmethod
    def get_for_tool(cls, requires: str, verbose: bool = False,
                     env_vars: Optional[Dict[str, str]] = None) -> Optional[Builder]:
        """
        Get a builder based on tool's 'requires' field.

        Args:
            requires: The dependency string (e.g., "msbuild", "dotnet")
            verbose: Enable verbose output
            env_vars: Environment variables to set during build

        Returns:
            Builder instance or None if not supported
        """
        mapping = {
            "msbuild": BuildSystem.MSBUILD,
            "dotnet": BuildSystem.DOTNET,
        }

        build_system = mapping.get(requires.lower())
        if build_system is None:
            return None

        return cls.create(build_system, verbose, env_vars)

    @classmethod
    def list_available(cls) -> Dict[str, bool]:
        """List all registered build systems and their availability."""
        result = {}
        for build_system, builder_class in cls._builders.items():
            builder = builder_class()
            result[build_system.value] = builder.is_available()
        return result


def get_builder(requires: str, verbose: bool = False,
                env_vars: Optional[Dict[str, str]] = None) -> Optional[Builder]:
    """
    Convenience function to get a builder for a tool requirement.

    Args:
        requires: The dependency string (e.g., "msbuild", "dotnet")
        verbose: Enable verbose output
        env_vars: Environment variables to set during build

    Returns:
        Builder instance or None if not supported
    """
    return BuilderFactory.get_for_tool(requires, verbose, env_vars)
