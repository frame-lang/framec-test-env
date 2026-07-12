#!/usr/bin/env python3
"""
Coverage enforcement: every fixture stem under tests/common/positive/<dir>/
must have exactly one file per supported backend, either as a real port
(`<stem>.f<ext>`) or as a markdown skip placeholder
(`<stem>.f<ext>.skip.md`) — but NOT both.

A skip placeholder's contents document why the fixture is intentionally
absent for that backend — capability-matrix skip, pending cookbook
port, etc.

Two failure modes are reported:
  - missing:    a backend has neither a real port nor a skip.md.
  - collision:  a backend has BOTH (a stale skip.md usually left behind
                when the backend later got a real port — drop it).

Erlang (`ferl`) is deprecated and not enforced (see BACKENDS). Helper
files (`.driver`, `.escript`, `README`, `run_tests`, etc.) are ignored.

Run: ./scripts/check_coverage.py
Exit 0 if clean, exit 1 on any missing file or collision.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

# The supported backends, by file extension. Erlang (`ferl`) is deprecated
# (being retired) and intentionally NOT enforced by the gate — its existing
# `.ferl` fixtures and `.ferl.skip.md` placeholders are ignored here. Re-add
# "ferl" if the deprecation is reversed.
BACKENDS: tuple[str, ...] = (
    "fc", "fcpp", "fcs", "fdart", "fgd", "fgo", "fjava",
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


def check_category(category: Path) -> tuple[list[str], list[str]]:
    """
    Return (missing, collisions) for one category dir.

    - missing:    "<relpath>/<stem>.<backend>" that has neither a real port
      nor a skip.md.
    - collisions: "<relpath>/<stem>.<backend>" that has BOTH a real port and
      a skip.md — a semantic error (usually a stale skip.md left behind when
      a backend later got a real port).
    """
    real: dict[str, set[str]] = defaultdict(set)
    skip: dict[str, set[str]] = defaultdict(set)

    for child in category.iterdir():
        if not child.is_file():
            continue
        result = categorize(child.name)
        if result is None:
            continue
        stem, backend, is_skip = result
        (skip if is_skip else real)[stem].add(backend)

    relpath = category.relative_to(category.parent.parent)
    missing: list[str] = []
    collisions: list[str] = []
    for stem in sorted(set(real) | set(skip)):
        present = real[stem] | skip[stem]
        for backend in BACKENDS:
            if backend not in present:
                missing.append(f"{relpath}/{stem}.{backend}")
        for backend in sorted(real[stem] & skip[stem]):
            collisions.append(f"{relpath}/{stem}.{backend}")
    return missing, collisions


def main(argv: list[str]) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    positive_dir = repo_root / "tests" / "common" / "positive"

    if not positive_dir.is_dir():
        print(f"ERROR: not found: {positive_dir}", file=sys.stderr)
        return 2

    all_missing: list[str] = []
    all_collisions: list[str] = []
    for category in sorted(positive_dir.iterdir()):
        if not category.is_dir():
            continue
        missing, collisions = check_category(category)
        all_missing.extend(missing)
        all_collisions.extend(collisions)

    n = len(BACKENDS)
    if not all_missing and not all_collisions:
        print(f"OK: every fixture stem has {n} files (real port or .skip).")
        return 0

    if all_collisions:
        print(f"FAIL: {len(all_collisions)} stem/backend(s) have BOTH a real "
              f"fixture and a .skip.md (drop the stale placeholder):")
        print()
        for entry in all_collisions:
            print(f"  {entry}  +  {entry}.skip.md")
        print()

    if all_missing:
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
