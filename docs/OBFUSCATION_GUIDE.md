# Obfuscation Automation Guide for WinBins

This document provides comprehensive suggestions and implementation ideas for automating obfuscation of compiled binaries and source code in the WinBins toolkit.

## Table of Contents

1. [Overview](#overview)
2. [Source Code Obfuscation](#source-code-obfuscation)
3. [Binary Obfuscation](#binary-obfuscation)
4. [Automation Pipeline](#automation-pipeline)
5. [Implementation Examples](#implementation-examples)
6. [Tool Recommendations](#tool-recommendations)
7. [Best Practices](#best-practices)

---

## Overview

Obfuscation in the context of authorized security testing helps:
- Avoid signature-based detection during pentesting engagements
- Test detection capabilities of security solutions
- Simulate real-world threat actor techniques
- Validate defense-in-depth strategies

**Important**: Only use these techniques in authorized testing scenarios with proper written authorization.

---

## Source Code Obfuscation

### 1. Name Mangling / Symbol Renaming

Rename functions, classes, variables, and method names to meaningless identifiers.

```python
# Example implementation for C# source
class NameMangler:
    def __init__(self, seed=None):
        self.mapping = {}
        self.random = random.Random(seed)

    def mangle(self, original_name):
        if original_name not in self.mapping:
            # Generate random name starting with letter
            new_name = ''.join(
                self.random.choices(string.ascii_letters, k=1) +
                self.random.choices(string.ascii_letters + string.digits, k=15)
            )
            self.mapping[original_name] = new_name
        return self.mapping[original_name]
```

**Regex patterns for C# symbol detection:**
```python
PATTERNS = {
    'class': r'class\s+([A-Z][a-zA-Z0-9_]*)',
    'method': r'(public|private|protected|internal)\s+\w+\s+([A-Z][a-zA-Z0-9_]*)\s*\(',
    'variable': r'\b(var|string|int|bool)\s+([a-z][a-zA-Z0-9_]*)\s*[=;]',
    'namespace': r'namespace\s+([A-Za-z][A-Za-z0-9_.]*)',
}
```

### 2. String Encryption

Encrypt string literals at compile time, decrypt at runtime.

```csharp
// Pre-obfuscation
string apiUrl = "https://api.example.com/endpoint";

// Post-obfuscation (XOR example)
byte[] encryptedUrl = new byte[] { 0x5B, 0x47, ... };  // XOR encrypted
string apiUrl = DecryptString(encryptedUrl, key);
```

**Python automation script:**
```python
def encrypt_strings_in_source(source_code, key):
    """Find and encrypt all string literals in source code."""
    string_pattern = r'"([^"\\]*(\\.[^"\\]*)*)"'

    def replace_string(match):
        original = match.group(1)
        encrypted = xor_encrypt(original.encode(), key)
        return f'Decrypt(new byte[]{{{", ".join(map(str, encrypted))}}}, key)'

    return re.sub(string_pattern, replace_string, source_code)
```

### 3. Control Flow Obfuscation

Add fake conditional branches, opaque predicates, and flattened control flow.

```csharp
// Original
if (condition) { DoA(); } else { DoB(); }

// Obfuscated with opaque predicate
int x = 7 * 11;  // Always 77
if ((x * x - 5929) == 0) {  // Always true (opaque predicate)
    if (condition) { DoA(); } else { DoB(); }
}
```

### 4. Dead Code Injection

Insert unreachable code paths to confuse analysis.

```python
def inject_dead_code(source_code):
    """Inject dead code blocks randomly."""
    dead_code_templates = [
        'if (false) {{ int {var} = {val}; }}',
        'while (1 == 2) {{ {var} = {val}; break; }}',
        '{{ int {var} = {val}; if ({var} < -999999) return; }}'
    ]
    # Insert at random positions...
```

---

## Binary Obfuscation

### 1. PE Metadata Modification

Remove or modify PE metadata that could be used for detection.

```python
import pefile

def strip_metadata(exe_path, output_path):
    """Strip debug information and modify metadata."""
    pe = pefile.PE(exe_path)

    # Remove debug directory
    if hasattr(pe, 'DIRECTORY_ENTRY_DEBUG'):
        pe.DIRECTORY_ENTRY_DEBUG = []

    # Modify timestamps
    pe.FILE_HEADER.TimeDateStamp = random.randint(0, 2**32)

    # Remove version info (optional)
    # pe.VS_VERSIONINFO = None

    pe.write(output_path)
```

### 2. Section Encryption

Encrypt specific sections and decrypt at runtime.

```python
def encrypt_section(pe, section_name, key):
    """Encrypt a PE section."""
    for section in pe.sections:
        if section.Name.rstrip(b'\x00') == section_name.encode():
            data = section.get_data()
            encrypted = aes_encrypt(data, key)
            # Write encrypted data and add decryption stub
```

### 3. Import Table Obfuscation

Hide imported functions using dynamic resolution.

```python
# Instead of: kernel32.dll!CreateProcessA
# Use: GetProcAddress(LoadLibraryA("kernel32.dll"), "CreateProcessA")

def obfuscate_imports(pe_path):
    """Replace static imports with dynamic resolution."""
    # 1. Parse IAT (Import Address Table)
    # 2. Generate dynamic resolution stubs
    # 3. Patch binary to use stubs
```

### 4. Packing/Compression

Compress the binary and add a runtime decompressor.

**Using UPX programmatically:**
```python
def pack_binary(input_path, output_path):
    """Pack binary using UPX."""
    subprocess.run([
        'upx', '--best', '--ultra-brute',
        '-o', output_path, input_path
    ], check=True)
```

**Custom packer approach:**
```python
def create_packed_binary(payload_path, stub_path, output_path):
    """Create custom packed binary."""
    # 1. Read and compress payload
    with open(payload_path, 'rb') as f:
        payload = zlib.compress(f.read(), level=9)

    # 2. Embed in stub that decompresses and executes
    # 3. Write final binary
```

---

## Automation Pipeline

### Suggested Pipeline Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Git Clone     │ ──> │ Source Obfuscate │ ──> │     Build       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                                                         v
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Output Binary  │ <── │ Binary Obfuscate │ <── │  Compile Check  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Configuration File Format

```yaml
# obfuscation_config.yaml
obfuscation:
  enabled: true

  source:
    name_mangling:
      enabled: true
      preserve_public_api: true
      seed: null  # Random if null

    string_encryption:
      enabled: true
      method: "xor"  # xor, aes, base64
      key_derivation: "random"

    control_flow:
      enabled: false
      complexity: "medium"

    dead_code:
      enabled: true
      density: 0.1  # 10% of code blocks

  binary:
    metadata_strip:
      enabled: true
      remove_debug: true
      randomize_timestamp: true

    packing:
      enabled: false
      packer: "upx"

    import_obfuscation:
      enabled: true
      method: "dynamic_resolution"

# Per-tool overrides
tools:
  rubeus:
    obfuscation:
      string_encryption:
        enabled: true
        method: "aes"

  mimikatz:
    obfuscation:
      enabled: false  # Already has protections
```

---

## Implementation Examples

### Example: Complete Obfuscation Class

```python
# winbins/obfuscation/csharp_obfuscator.py

import re
import random
import string
import hashlib
from pathlib import Path
from typing import Dict, List, Set

class CSharpObfuscator:
    """Obfuscator for C# source code."""

    def __init__(self, config: dict):
        self.config = config
        self.name_map: Dict[str, str] = {}
        self.preserved_names: Set[str] = {
            'Main', 'ToString', 'Equals', 'GetHashCode',
            'Dispose', 'InitializeComponent'
        }

    def generate_name(self, length: int = 12) -> str:
        """Generate random identifier."""
        first = random.choice(string.ascii_letters)
        rest = ''.join(random.choices(
            string.ascii_letters + string.digits, k=length-1
        ))
        return first + rest

    def mangle_name(self, original: str) -> str:
        """Get or create mangled name for identifier."""
        if original in self.preserved_names:
            return original
        if original not in self.name_map:
            self.name_map[original] = self.generate_name()
        return self.name_map[original]

    def obfuscate_file(self, source_path: Path) -> str:
        """Obfuscate a single C# source file."""
        content = source_path.read_text()

        if self.config.get('name_mangling', {}).get('enabled', True):
            content = self._mangle_identifiers(content)

        if self.config.get('string_encryption', {}).get('enabled', False):
            content = self._encrypt_strings(content)

        if self.config.get('dead_code', {}).get('enabled', False):
            content = self._inject_dead_code(content)

        return content

    def _mangle_identifiers(self, content: str) -> str:
        """Rename identifiers in source code."""
        # Class names
        content = re.sub(
            r'\bclass\s+([A-Z][a-zA-Z0-9_]*)',
            lambda m: f'class {self.mangle_name(m.group(1))}',
            content
        )

        # Method names (simplified)
        content = re.sub(
            r'\b(void|string|int|bool|Task)\s+([A-Z][a-zA-Z0-9_]*)\s*\(',
            lambda m: f'{m.group(1)} {self.mangle_name(m.group(2))}(',
            content
        )

        return content

    def _encrypt_strings(self, content: str) -> str:
        """Encrypt string literals."""
        key = random.randbytes(16)

        def encrypt_match(match):
            original = match.group(1)
            encrypted = self._xor_encrypt(original.encode(), key)
            bytes_str = ', '.join(f'0x{b:02X}' for b in encrypted)
            return f'_D(new byte[]{{{bytes_str}}})'

        # Add decryption helper method
        helper = self._generate_decrypt_helper(key)

        # Replace strings
        content = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', encrypt_match, content)

        # Insert helper at class level
        content = re.sub(
            r'(class\s+\w+\s*{)',
            f'\\1\n{helper}',
            content,
            count=1
        )

        return content

    def _xor_encrypt(self, data: bytes, key: bytes) -> bytes:
        """XOR encrypt data."""
        return bytes(d ^ key[i % len(key)] for i, d in enumerate(data))

    def _generate_decrypt_helper(self, key: bytes) -> str:
        """Generate decryption helper method."""
        key_str = ', '.join(f'0x{b:02X}' for b in key)
        return f'''
        private static byte[] _k = new byte[]{{{key_str}}};
        private static string _D(byte[] d) {{
            byte[] r = new byte[d.Length];
            for(int i = 0; i < d.Length; i++) r[i] = (byte)(d[i] ^ _k[i % _k.Length]);
            return System.Text.Encoding.UTF8.GetString(r);
        }}
        '''

    def _inject_dead_code(self, content: str) -> str:
        """Insert dead code blocks."""
        dead_blocks = [
            'if (Environment.TickCount < -1) { Console.Write(""); }',
            'if (false) { int _ = 0; }',
            'while (1 == 2) { break; }',
        ]

        # Insert after opening braces of methods
        def insert_dead(match):
            return match.group(0) + '\n' + random.choice(dead_blocks)

        content = re.sub(
            r'(\)\s*{)(\s*\n)',
            insert_dead,
            content,
            count=int(content.count(') {') * 0.3)  # 30% of methods
        )

        return content

    def get_mapping(self) -> Dict[str, str]:
        """Return the name mapping for debugging/reversal."""
        return self.name_map.copy()
```

### Example: Binary Post-Processor

```python
# winbins/obfuscation/binary_processor.py

import struct
import random
from pathlib import Path

class BinaryProcessor:
    """Post-process compiled binaries for evasion."""

    def __init__(self, config: dict):
        self.config = config

    def process(self, binary_path: Path, output_path: Path) -> bool:
        """Apply all configured binary transformations."""
        data = bytearray(binary_path.read_bytes())

        if self.config.get('randomize_timestamp', True):
            data = self._randomize_timestamp(data)

        if self.config.get('modify_rich_header', True):
            data = self._modify_rich_header(data)

        if self.config.get('add_fake_sections', False):
            data = self._add_fake_sections(data)

        output_path.write_bytes(data)
        return True

    def _randomize_timestamp(self, data: bytearray) -> bytearray:
        """Randomize PE timestamp."""
        # PE signature offset at 0x3C
        pe_offset = struct.unpack('<I', data[0x3C:0x40])[0]
        # Timestamp at PE + 8
        timestamp_offset = pe_offset + 8
        new_timestamp = random.randint(0x50000000, 0x67000000)
        struct.pack_into('<I', data, timestamp_offset, new_timestamp)
        return data

    def _modify_rich_header(self, data: bytearray) -> bytearray:
        """Modify or remove Rich header."""
        # Find Rich header marker
        rich_marker = b'Rich'
        pos = data.find(rich_marker)
        if pos > 0:
            # XOR with different key or zero out
            # (simplified - real implementation needs proper Rich parsing)
            for i in range(0x80, pos):
                data[i] = random.randint(0, 255)
        return data

    def _add_fake_sections(self, data: bytearray) -> bytearray:
        """Add fake PE sections (advanced)."""
        # This is complex and requires proper PE manipulation
        # Consider using pefile library for real implementation
        return data
```

---

## Tool Recommendations

### Existing Obfuscation Tools to Integrate

| Tool | Type | Language | Purpose |
|------|------|----------|---------|
| **ConfuserEx** | Source | C# | .NET assembly obfuscation |
| **Dotfuscator** | Source | C# | Commercial .NET obfuscator |
| **ILProtector** | Binary | .NET | IL code protection |
| **Themida** | Binary | Any | Commercial packer/protector |
| **VMProtect** | Binary | Any | Virtualization-based protection |
| **UPX** | Binary | Any | Compression/packing |
| **LLVM-Obfuscator** | Source | C/C++ | LLVM-based obfuscation |

### Open-Source Integration Targets

```python
OBFUSCATION_TOOLS = {
    "confuserex": {
        "repo": "https://github.com/yck1509/ConfuserEx.git",
        "build_cmd": ["msbuild", "ConfuserEx.sln", "/p:Configuration=Release"],
        "cli": "Confuser.CLI.exe",
        "supports": [".NET"],
    },
    "net-reactor": {
        "type": "commercial",
        "supports": [".NET"],
        "integration": "cli",
    },
}
```

---

## Best Practices

### 1. Layered Obfuscation
Apply multiple techniques in sequence for better protection:
```
Source Obfuscation → Compile → Binary Obfuscation → Pack
```

### 2. Preserve Functionality
- Always test obfuscated binaries
- Maintain mapping files for debugging
- Use CI/CD to verify functionality

### 3. Avoid Over-Obfuscation
- Some techniques conflict with each other
- Heavy obfuscation can cause performance issues
- Balance protection vs. usability

### 4. Signature Management
- Rotate obfuscation seeds regularly
- Create unique builds per engagement
- Track which builds are used where

### 5. Legal Compliance
- Document authorization for each engagement
- Maintain audit trails
- Follow responsible disclosure

---

## Future Implementation Roadmap

1. **Phase 1**: Basic name mangling and string encryption
2. **Phase 2**: Binary metadata modification
3. **Phase 3**: Integration with ConfuserEx
4. **Phase 4**: Custom packer implementation
5. **Phase 5**: Advanced control flow obfuscation
6. **Phase 6**: Machine learning-based evasion testing

---

## References

- [ConfuserEx Documentation](https://github.com/yck1509/ConfuserEx/wiki)
- [PE Format Specification](https://docs.microsoft.com/en-us/windows/win32/debug/pe-format)
- [.NET Assembly Obfuscation Techniques](https://www.codeproject.com/Articles/29112/NET-Obfuscation)
- [MITRE ATT&CK - Defense Evasion](https://attack.mitre.org/tactics/TA0005/)
