"""
Base obfuscation interfaces and classes for WinBins.
Provides framework for implementing various obfuscation techniques.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import secrets
import string


class ObfuscationType(Enum):
    """Types of obfuscation supported."""
    NAME_MANGLING = "name_mangling"        # Rename functions, classes, variables
    STRING_ENCRYPTION = "string_encryption"  # Encrypt string literals
    CONTROL_FLOW = "control_flow"           # Obfuscate control flow
    DEAD_CODE = "dead_code"                 # Insert dead code
    METADATA_STRIP = "metadata_strip"       # Remove debug/metadata
    PACKING = "packing"                     # Pack/compress binary
    RESOURCE_ENCRYPTION = "resource_encryption"  # Encrypt resources


@dataclass
class ObfuscationConfig:
    """Configuration for obfuscation operations."""
    enabled_types: List[ObfuscationType] = field(default_factory=list)
    preserve_entry_points: bool = True
    random_seed: Optional[int] = None
    name_prefix: str = ""
    name_suffix: str = ""
    min_name_length: int = 8
    max_name_length: int = 16
    encryption_key: Optional[bytes] = None
    custom_options: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.enabled_types:
            self.enabled_types = [ObfuscationType.NAME_MANGLING]


@dataclass
class ObfuscationResult:
    """Result of an obfuscation operation."""
    success: bool
    input_path: Path
    output_path: Optional[Path] = None
    original_hash: str = ""
    obfuscated_hash: str = ""
    types_applied: List[ObfuscationType] = field(default_factory=list)
    mappings: Dict[str, str] = field(default_factory=dict)  # Original -> obfuscated name mappings
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)


class NameGenerator:
    """Generates obfuscated names for symbols."""

    def __init__(self, seed: Optional[int] = None,
                 min_length: int = 8, max_length: int = 16,
                 prefix: str = "", suffix: str = ""):
        self.min_length = min_length
        self.max_length = max_length
        self.prefix = prefix
        self.suffix = suffix
        self._used_names: set = set()
        self._seed = seed

        if seed is not None:
            import random
            # Create a new Random instance with the seed (not global state)
            self._random = random.Random(seed)
        else:
            self._random = secrets.SystemRandom()

    def generate(self) -> str:
        """Generate a unique obfuscated name."""
        while True:
            length = self._random.randint(self.min_length, self.max_length)
            # Start with letter, rest can be alphanumeric
            name = self._random.choice(string.ascii_letters)
            name += ''.join(
                self._random.choices(string.ascii_letters + string.digits, k=length - 1)
            )
            full_name = f"{self.prefix}{name}{self.suffix}"

            if full_name not in self._used_names:
                self._used_names.add(full_name)
                return full_name

    def generate_mapping(self, original_names: List[str]) -> Dict[str, str]:
        """Generate a mapping of original names to obfuscated names."""
        return {name: self.generate() for name in original_names}

    def reset(self) -> None:
        """Reset used names."""
        self._used_names.clear()


class Obfuscator(ABC):
    """Abstract base class for obfuscators."""

    def __init__(self, config: Optional[ObfuscationConfig] = None):
        self.config = config or ObfuscationConfig()
        self.name_generator = NameGenerator(
            seed=self.config.random_seed,
            min_length=self.config.min_name_length,
            max_length=self.config.max_name_length,
            prefix=self.config.name_prefix,
            suffix=self.config.name_suffix,
        )

    @property
    @abstractmethod
    def name(self) -> str:
        """Return obfuscator name."""
        pass

    @property
    @abstractmethod
    def supported_types(self) -> List[ObfuscationType]:
        """Return list of supported obfuscation types."""
        pass

    @abstractmethod
    def obfuscate(self, input_path: Path, output_path: Path) -> ObfuscationResult:
        """
        Perform obfuscation on input file.

        Args:
            input_path: Path to input file
            output_path: Path for obfuscated output

        Returns:
            ObfuscationResult with details of operation
        """
        pass

    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def validate_config(self) -> List[str]:
        """Validate configuration, return list of warnings."""
        warnings = []

        for obf_type in self.config.enabled_types:
            if obf_type not in self.supported_types:
                warnings.append(
                    f"Obfuscation type {obf_type.value} not supported by {self.name}"
                )

        return warnings


class SourceCodeObfuscator(Obfuscator):
    """Base class for source code obfuscators."""

    @property
    def supported_types(self) -> List[ObfuscationType]:
        return [
            ObfuscationType.NAME_MANGLING,
            ObfuscationType.STRING_ENCRYPTION,
            ObfuscationType.DEAD_CODE,
            ObfuscationType.CONTROL_FLOW,
        ]

    def obfuscate(self, input_path: Path, output_path: Path) -> ObfuscationResult:
        """Placeholder implementation - override in subclasses."""
        return ObfuscationResult(
            success=False,
            input_path=input_path,
            error_message="Not implemented - override in subclass"
        )


class BinaryObfuscator(Obfuscator):
    """Base class for binary obfuscators."""

    @property
    def supported_types(self) -> List[ObfuscationType]:
        return [
            ObfuscationType.METADATA_STRIP,
            ObfuscationType.PACKING,
            ObfuscationType.RESOURCE_ENCRYPTION,
        ]

    def obfuscate(self, input_path: Path, output_path: Path) -> ObfuscationResult:
        """Placeholder implementation - override in subclasses."""
        return ObfuscationResult(
            success=False,
            input_path=input_path,
            error_message="Not implemented - override in subclass"
        )
