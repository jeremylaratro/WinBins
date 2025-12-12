"""
Tests for the obfuscation module.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from winbins.obfuscation.base import (
    ObfuscationType,
    ObfuscationConfig,
    ObfuscationResult,
    NameGenerator,
    Obfuscator,
    SourceCodeObfuscator,
    BinaryObfuscator,
)


class TestObfuscationType:
    """Tests for ObfuscationType enum."""

    def test_all_types_exist(self):
        """Test all obfuscation types are defined."""
        types = [
            "NAME_MANGLING",
            "STRING_ENCRYPTION",
            "CONTROL_FLOW",
            "DEAD_CODE",
            "METADATA_STRIP",
            "PACKING",
            "RESOURCE_ENCRYPTION",
        ]
        for obf_type in types:
            assert ObfuscationType[obf_type] is not None


class TestObfuscationConfig:
    """Tests for ObfuscationConfig dataclass."""

    def test_default_config(self):
        """Test default configuration."""
        config = ObfuscationConfig()

        assert config.preserve_entry_points is True
        assert config.min_name_length == 8
        assert config.max_name_length == 16
        assert ObfuscationType.NAME_MANGLING in config.enabled_types

    def test_custom_config(self):
        """Test custom configuration."""
        config = ObfuscationConfig(
            enabled_types=[ObfuscationType.STRING_ENCRYPTION],
            min_name_length=12,
            max_name_length=20,
            name_prefix="_obf_",
        )

        assert config.min_name_length == 12
        assert config.max_name_length == 20
        assert config.name_prefix == "_obf_"
        assert ObfuscationType.STRING_ENCRYPTION in config.enabled_types


class TestObfuscationResult:
    """Tests for ObfuscationResult dataclass."""

    def test_success_result(self, temp_dir):
        """Test successful obfuscation result."""
        result = ObfuscationResult(
            success=True,
            input_path=temp_dir / "input.exe",
            output_path=temp_dir / "output.exe",
            original_hash="abc123",
            obfuscated_hash="def456",
            types_applied=[ObfuscationType.NAME_MANGLING],
        )

        assert result.success is True
        assert result.types_applied == [ObfuscationType.NAME_MANGLING]

    def test_failed_result(self, temp_dir):
        """Test failed obfuscation result."""
        result = ObfuscationResult(
            success=False,
            input_path=temp_dir / "input.exe",
            error_message="Obfuscation failed",
        )

        assert result.success is False
        assert result.error_message == "Obfuscation failed"

    def test_result_with_mappings(self, temp_dir):
        """Test result with name mappings."""
        result = ObfuscationResult(
            success=True,
            input_path=temp_dir / "input.exe",
            mappings={
                "originalFunc": "xYz123AbC",
                "MyClass": "qWe456DeF",
            }
        )

        assert len(result.mappings) == 2
        assert "originalFunc" in result.mappings


class TestNameGenerator:
    """Tests for NameGenerator class."""

    def test_generate_unique_names(self):
        """Test generating unique names."""
        generator = NameGenerator()
        names = set()

        for _ in range(100):
            name = generator.generate()
            assert name not in names
            names.add(name)

    def test_name_length(self):
        """Test generated name length."""
        generator = NameGenerator(min_length=10, max_length=15)

        for _ in range(50):
            name = generator.generate()
            assert 10 <= len(name) <= 15

    def test_name_with_prefix_suffix(self):
        """Test name generation with prefix and suffix."""
        generator = NameGenerator(prefix="_pre_", suffix="_suf")
        name = generator.generate()

        assert name.startswith("_pre_")
        assert name.endswith("_suf")

    def test_name_starts_with_letter(self):
        """Test name starts with letter (valid identifier)."""
        generator = NameGenerator()

        for _ in range(50):
            name = generator.generate()
            # After removing prefix, should start with letter
            assert name[0].isalpha()

    def test_deterministic_with_seed(self):
        """Test deterministic generation with seed."""
        gen1 = NameGenerator(seed=42)
        gen2 = NameGenerator(seed=42)

        names1 = [gen1.generate() for _ in range(10)]
        names2 = [gen2.generate() for _ in range(10)]

        assert names1 == names2

    def test_generate_mapping(self):
        """Test generating name mappings."""
        generator = NameGenerator()
        original_names = ["func1", "func2", "MyClass"]

        mapping = generator.generate_mapping(original_names)

        assert len(mapping) == 3
        assert "func1" in mapping
        assert "func2" in mapping
        assert "MyClass" in mapping
        # All mapped names should be different
        assert len(set(mapping.values())) == 3

    def test_reset(self):
        """Test resetting used names."""
        generator = NameGenerator(seed=42)

        name1 = generator.generate()
        generator.reset()
        # After reset with same seed, should get same name
        generator = NameGenerator(seed=42)
        name2 = generator.generate()

        assert name1 == name2


class TestSourceCodeObfuscator:
    """Tests for SourceCodeObfuscator class."""

    def test_supported_types(self):
        """Test supported obfuscation types."""
        class ConcreteObfuscator(SourceCodeObfuscator):
            @property
            def name(self):
                return "Test"

        obfuscator = ConcreteObfuscator()
        supported = obfuscator.supported_types

        assert ObfuscationType.NAME_MANGLING in supported
        assert ObfuscationType.STRING_ENCRYPTION in supported
        assert ObfuscationType.DEAD_CODE in supported
        assert ObfuscationType.CONTROL_FLOW in supported

    def test_validate_config_warnings(self):
        """Test config validation returns warnings for unsupported types."""
        class ConcreteObfuscator(SourceCodeObfuscator):
            @property
            def name(self):
                return "Test"

        config = ObfuscationConfig(
            enabled_types=[ObfuscationType.PACKING]  # Not supported for source
        )
        obfuscator = ConcreteObfuscator(config)
        warnings = obfuscator.validate_config()

        assert len(warnings) > 0


class TestBinaryObfuscator:
    """Tests for BinaryObfuscator class."""

    def test_supported_types(self):
        """Test supported obfuscation types."""
        class ConcreteObfuscator(BinaryObfuscator):
            @property
            def name(self):
                return "Test"

        obfuscator = ConcreteObfuscator()
        supported = obfuscator.supported_types

        assert ObfuscationType.METADATA_STRIP in supported
        assert ObfuscationType.PACKING in supported
        assert ObfuscationType.RESOURCE_ENCRYPTION in supported

    def test_compute_hash(self, temp_dir):
        """Test computing file hash."""
        class ConcreteObfuscator(BinaryObfuscator):
            @property
            def name(self):
                return "Test"

        test_file = temp_dir / "test.bin"
        test_file.write_bytes(b"test content")

        obfuscator = ConcreteObfuscator()
        hash_value = obfuscator.compute_hash(test_file)

        assert len(hash_value) == 64  # SHA256 hex length
        assert hash_value.isalnum()
