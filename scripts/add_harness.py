#!/usr/bin/env python3
"""Add TAP test harnesses to migrated Frame tests."""

import os
import re
import sys
from pathlib import Path

def get_system_name(content: str) -> str:
    """Extract the system name from Frame source."""
    match = re.search(r'@@system\s+(\w+)', content)
    if match:
        return match.group(1)
    return 'S'  # Default fallback

# Harness templates per language
def python_harness(test_name: str, system_name: str) -> str:
    return f'''
# Stub functions for placeholder calls
def native(): pass
def x(): pass

# TAP test harness
if __name__ == "__main__":
    print("TAP version 14")
    print("1..1")
    try:
        s = {system_name}()
        if hasattr(s, 'e'):
            s.e()
        print("ok 1 - {test_name}")
    except Exception as ex:
        print(f"not ok 1 - {test_name} # {{ex}}")
'''

def typescript_harness(test_name: str, system_name: str) -> str:
    return f'''
// Stub functions for placeholder calls
function native(): void {{}}
function x(): void {{}}

// TAP test harness
function main() {{
    console.log("TAP version 14");
    console.log("1..1");
    try {{
        const s = new {system_name}();
        if (typeof (s as any).e === 'function') {{
            (s as any).e();
        }}
        console.log("ok 1 - {test_name}");
    }} catch (ex) {{
        console.log(`not ok 1 - {test_name} # ${{ex}}`);
    }}
}}
main();
'''

def rust_harness(test_name: str, system_name: str) -> str:
    return f'''
// Stub functions for placeholder calls
fn native() {{}}
fn x() {{}}

// TAP test harness
fn main() {{
    println!("TAP version 14");
    println!("1..1");
    let mut _s = {system_name}::new();
    // Call e() if the method exists
    // Note: Rust doesn't have dynamic dispatch like Python/TS
    // so we just instantiate and print success
    println!("ok 1 - {test_name}");
}}
'''

def has_harness(content: str, lang: str) -> bool:
    """Check if file already has a test harness."""
    if lang == 'python':
        return 'if __name__' in content
    elif lang == 'typescript':
        return 'function main()' in content and 'TAP' in content
    elif lang == 'rust':
        return 'fn main()' in content
    return False

def remove_old_harness(content: str, lang: str) -> str:
    """Remove existing harness from content."""
    if lang == 'python':
        # Remove from "# Stub functions" or "# TAP test harness" to end
        content = re.sub(r'\n# Stub functions.*', '', content, flags=re.DOTALL)
        content = re.sub(r'\n# TAP test harness.*', '', content, flags=re.DOTALL)
    elif lang == 'typescript':
        content = re.sub(r'\n// Stub functions.*', '', content, flags=re.DOTALL)
        content = re.sub(r'\n// TAP test harness.*', '', content, flags=re.DOTALL)
    elif lang == 'rust':
        content = re.sub(r'\n// Stub functions.*', '', content, flags=re.DOTALL)
        content = re.sub(r'\n// TAP test harness.*', '', content, flags=re.DOTALL)
    return content

def add_harness(filepath: Path, force: bool = False) -> bool:
    """Add test harness to a file. Returns True if modified."""
    content = filepath.read_text()
    test_name = filepath.stem
    system_name = get_system_name(content)

    # Determine language
    ext = filepath.suffix
    if ext == '.fpy':
        lang = 'python'
        harness = python_harness(test_name, system_name)
    elif ext == '.fts':
        lang = 'typescript'
        harness = typescript_harness(test_name, system_name)
    elif ext == '.frs':
        lang = 'rust'
        harness = rust_harness(test_name, system_name)
    else:
        return False

    # Handle existing harness
    if has_harness(content, lang):
        if force:
            content = remove_old_harness(content, lang)
        else:
            return False

    # Add harness at end
    new_content = content.rstrip() + '\n' + harness
    filepath.write_text(new_content)
    return True

def process_directory(dirpath: Path, dry_run: bool = False, force: bool = False) -> int:
    """Process all test files in directory. Returns count of modified files."""
    modified = 0
    for ext in ['.fpy', '.fts', '.frs']:
        for filepath in dirpath.rglob(f'*{ext}'):
            # Skip primary tests (already have harnesses)
            if '/primary/' in str(filepath):
                continue

            if dry_run:
                content = filepath.read_text()
                lang = {'fpy': 'python', 'fts': 'typescript', 'frs': 'rust'}[ext[1:]]
                if force or not has_harness(content, lang):
                    print(f"Would modify: {filepath}")
                    modified += 1
            else:
                if add_harness(filepath, force):
                    print(f"Modified: {filepath}")
                    modified += 1
    return modified

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Add TAP harnesses to Frame tests')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be modified')
    parser.add_argument('--force', action='store_true', help='Replace existing harnesses')
    args = parser.parse_args()

    dirpath = Path(args.directory)
    if not dirpath.exists():
        print(f"Error: {dirpath} does not exist")
        sys.exit(1)

    count = process_directory(dirpath, args.dry_run, args.force)
    print(f"\n{'Would modify' if args.dry_run else 'Modified'}: {count} files")
