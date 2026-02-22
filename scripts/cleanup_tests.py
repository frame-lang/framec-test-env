#!/usr/bin/env python3
"""Clean up test files - remove duplicate main functions, fix targets."""

import re
import sys
from pathlib import Path

def cleanup_rust(filepath: Path) -> bool:
    """Clean up Rust test file."""
    content = filepath.read_text()
    original = content

    # Remove old standalone main functions (not the TAP harness)
    content = re.sub(r'\nfn main\(\) \{ println!\("OK"\); \}\n', '\n', content)
    content = re.sub(r'\nfn main\(\) \{\s*println!\("OK"\);\s*\}\n', '\n', content)

    # Remove Python-specific directives from Rust files
    content = re.sub(r'@@py-compile\n', '', content)
    content = re.sub(r'@@compile-expect:.*def .*\n', '', content)

    if content != original:
        filepath.write_text(content)
        return True
    return False

def cleanup_typescript(filepath: Path) -> bool:
    """Clean up TypeScript test file."""
    content = filepath.read_text()
    original = content

    # Remove Python-specific directives
    content = re.sub(r'@@py-compile\n', '', content)
    content = re.sub(r'@@compile-expect:.*def .*\n', '', content)

    if content != original:
        filepath.write_text(content)
        return True
    return False

def cleanup_python(filepath: Path) -> bool:
    """Clean up Python test file."""
    content = filepath.read_text()
    original = content

    # Nothing specific to clean for Python
    if content != original:
        filepath.write_text(content)
        return True
    return False

def process_directory(dirpath: Path) -> int:
    """Process all test files in directory."""
    modified = 0

    for filepath in dirpath.rglob('*.frs'):
        if cleanup_rust(filepath):
            print(f"Cleaned: {filepath}")
            modified += 1

    for filepath in dirpath.rglob('*.fts'):
        if cleanup_typescript(filepath):
            print(f"Cleaned: {filepath}")
            modified += 1

    for filepath in dirpath.rglob('*.fpy'):
        if cleanup_python(filepath):
            print(f"Cleaned: {filepath}")
            modified += 1

    return modified

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: cleanup_tests.py <directory>")
        sys.exit(1)

    dirpath = Path(sys.argv[1])
    if not dirpath.exists():
        print(f"Error: {dirpath} does not exist")
        sys.exit(1)

    count = process_directory(dirpath)
    print(f"\nCleaned: {count} files")
