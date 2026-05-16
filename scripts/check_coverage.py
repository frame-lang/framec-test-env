#!/usr/bin/env python3
"""
Coverage enforcement: every fixture stem under tests/common/positive/<dir>/
must have exactly one file per supported backend, either as a real port
(`<stem>.f<ext>`) or as a markdown skip placeholder
(`<stem>.f<ext>.skip.md`).

A skip placeholder's contents document why the fixture is intentionally
absent for that backend — capability-matrix skip, pending cookbook
port, etc.

Helper files (`.driver`, `.escript`, `README`, `run_tests`, etc.) are
ignored.

Run: ./scripts/check_coverage.py
Exit 0 if clean, exit 1 if any stem is missing a file. Lists missing
files explicitly.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

# The 17 supported backends, by file extension.
BACKENDS: tuple[str, ...] = (
    "fc", "fcpp", "fcs", "fdart", "ferl", "fgd", "fgo", "fjava",
    "fjs", "fkt", "flua", "fphp", "fpy", "frb", "frs", "fswift", "fts",
)

# Extensions that exist alongside fixtures but are NOT themselves
# fixtures (drivers, escript sidecars, READMEs, etc.). Files matching
# these are ignored during enumeration.
IGNORED_SUFFIXES: tuple[str, ...] = (
    ".driver",
    ".driver.escript",
    ".escript",
    ".md",
    ".txt",
)
IGNORED_NAMES: frozenset[str] = frozenset({
    "README",
    "HSM_TEST_PLAN",
    "run_tests",
})


def categorize(filename: str) -> tuple[str, str, bool] | None:
    """
    Return (stem, backend, is_skip) for a fixture file, or None if the
    file is not a fixture.

    `<stem>.f<ext>`          → (stem, "f<ext>", False)
    `<stem>.f<ext>.skip.md`  → (stem, "f<ext>", True)
    anything else            → None
    """
    if filename in IGNORED_NAMES:
        return None

    # Try skip form first: <stem>.f<ext>.skip.md (must come before
    # the generic ".md" filter below or .skip.md files get dropped).
    if filename.endswith(".skip.md"):
        body = filename[:-len(".skip.md")]
        if "." not in body:
            return None
        stem, ext = body.rsplit(".", 1)
        if ext in BACKENDS:
            return (stem, ext, True)
        return None

    for suffix in IGNORED_SUFFIXES:
        if filename.endswith(suffix):
            return None

    # Real port: <stem>.f<ext>
    if "." not in filename:
        return None
    stem, ext = filename.rsplit(".", 1)
    if ext in BACKENDS:
        return (stem, ext, False)
    return None


def check_category(category: Path) -> list[str]:
    """
    Return list of missing-file descriptions for one category dir.
    Each item is a string suitable for printing.
    """
    # stem → set of backends with any file (real or skip)
    coverage: dict[str, set[str]] = defaultdict(set)

    for child in category.iterdir():
        if not child.is_file():
            continue
        result = categorize(child.name)
        if result is None:
            continue
        stem, backend, _is_skip = result
        coverage[stem].add(backend)

    missing: list[str] = []
    for stem in sorted(coverage):
        present = coverage[stem]
        absent = [b for b in BACKENDS if b not in present]
        if absent:
            relpath = category.relative_to(category.parent.parent)
            for backend in absent:
                missing.append(f"{relpath}/{stem}.{backend}")
    return missing


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    positive_dir = repo_root / "tests" / "common" / "positive"

    if not positive_dir.is_dir():
        print(f"ERROR: not found: {positive_dir}", file=sys.stderr)
        return 2

    all_missing: list[str] = []
    for category in sorted(positive_dir.iterdir()):
        if not category.is_dir():
            continue
        all_missing.extend(check_category(category))

    if not all_missing:
        print("OK: every fixture stem has 17 files (real port or .skip).")
        return 0

    print(f"FAIL: {len(all_missing)} fixture file(s) missing:")
    print()
    for entry in all_missing:
        print(f"  {entry}{{,.skip.md}}")
    print()
    print(
        "Each entry needs a real fixture file OR a `<name>.skip.md` "
        "markdown placeholder documenting why this backend is "
        "intentionally absent."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
