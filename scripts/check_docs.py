#!/usr/bin/env python3
"""
Doc-freshness gate: keep the human docs from drifting away from the code.

The *operational* source of truth for the backend set is the language
dispatch in `docker/runners/runner.sh` — that `case "$LANG"` block is what
actually maps a language to the framec `-t <target>` value, the `.f<ext>`
source extension, and the output extension. `scripts/check_coverage.py`
owns the *enforced* subset (its BACKENDS tuple; Erlang is deprecated and
intentionally excluded). Everything a human reads — the "Supported
Languages" table in README.md and the "N backends" counts scattered through
the guides — is derived here and verified against those two sources so a
stale table or an off-by-one count fails CI instead of misleading a reader.

Usage:
    python scripts/check_docs.py          # verify; exit 1 on any drift
    python scripts/check_docs.py --fix     # rewrite docs to match the code

Structural columns (Extension, Target Name, whether a row exists, and the
Deprecated flag) are code-derived and enforced. The Stable/Experimental
Status is editorial — it is preserved from the current table and only
checked for the one invariant that must hold: a deprecated backend is
marked Deprecated and an enforced one is not.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNNER = REPO / "docker" / "runners" / "runner.sh"
README = REPO / "README.md"

# Import the enforced subset straight from the gate so there is exactly one
# definition of "which backends the coverage gate requires".
sys.path.insert(0, str(REPO / "scripts"))
import check_coverage  # noqa: E402  (path set above)

ENFORCED: frozenset[str] = frozenset(check_coverage.BACKENDS)


@dataclass(frozen=True)
class Backend:
    language: str   # framec target language key, e.g. "python"
    target: str     # value passed to framec -t, e.g. "python_3"
    ext: str        # source extension without dot, e.g. "fpy"
    out_ext: str    # transpiled-file extension, e.g. "py"

    @property
    def enforced(self) -> bool:
        return self.ext in ENFORCED


# ── source-of-truth parsing ────────────────────────────────────────────────

# Matches one dispatch line, e.g.:
#     python)     target="python_3";  ext="fpy"; out_ext="py" ;;
_DISPATCH_RE = re.compile(
    r'^\s*(?P<lang>\w+)\)\s*'
    r'target="(?P<target>[^"]+)";\s*'
    r'ext="(?P<ext>[^"]+)";\s*'
    r'out_ext="(?P<out_ext>[^"]+)"'
)


def load_backends() -> list[Backend]:
    """Parse the `case "$LANG"` dispatch in runner.sh, in file order."""
    text = RUNNER.read_text()
    # Restrict to the language-configuration case block so we never pick up
    # an unrelated `target="..."` assignment elsewhere in the script.
    start = text.find('case "$LANG" in')
    if start == -1:
        raise SystemExit(f"could not find language case block in {RUNNER}")
    block = text[start:]
    esac = block.find("\nesac")
    if esac != -1:
        block = block[:esac]

    backends: list[Backend] = []
    for line in block.splitlines():
        m = _DISPATCH_RE.match(line)
        if m:
            backends.append(Backend(
                language=m.group("lang"),
                target=m.group("target"),
                ext=m.group("ext"),
                out_ext=m.group("out_ext"),
            ))
    if not backends:
        raise SystemExit(f"parsed zero backends from {RUNNER}")
    return backends


# ── README "Supported Languages" table ─────────────────────────────────────

_TABLE_HEADER = "| Language | Extension | Target Name | Status |"
_TABLE_SEP = "|---|---|---|---|"


def current_status_map(readme: str) -> dict[str, str]:
    """Read the existing Status cell per extension so --fix preserves the
    editorial Stable/Experimental judgement (Deprecated is re-derived)."""
    status: dict[str, str] = {}
    # Cell-based parse of the table rows.
    for line in readme.splitlines():
        if line.startswith("|") and "`.f" in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) == 4:
                ext = cells[1].strip("`").lstrip(".")
                status[ext] = cells[3]
    return status


def render_table(backends: list[Backend], status: dict[str, str]) -> str:
    lines = [_TABLE_HEADER, _TABLE_SEP]
    for b in backends:
        if not b.enforced:
            st = "Deprecated (being retired this release)"
        else:
            st = status.get(b.ext, "Experimental")
            # An enforced backend must never carry a Deprecated status.
            if "Deprecated" in st:
                st = "Experimental"
        lang_disp = _LANG_DISPLAY.get(b.language, b.language.capitalize())
        lines.append(f"| {lang_disp} | `.{b.ext}` | `{b.target}` | {st} |")
    return "\n".join(lines)


# Display names that are not a plain .capitalize() of the language key.
_LANG_DISPLAY = {
    "cpp": "C++",
    "csharp": "C#",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "php": "PHP",
    "gdscript": "GDScript",
    "c": "C",
}


def replace_table(readme: str, new_table: str) -> str:
    """Swap the table that sits under the '## Supported Languages' heading."""
    m = re.search(r"(## Supported Languages\s*\n+)(\| Language \|.*?\n)(?=\n#|\Z)",
                  readme, re.DOTALL)
    if not m:
        raise SystemExit("could not locate the Supported Languages table in README.md")
    return readme[:m.start(2)] + new_table + "\n" + readme[m.end(2):]


# ── numeric count invariants ───────────────────────────────────────────────
# Each rule: (glob, compiled pattern with one \d+ group, expected value, label).
# GATE sentences describe the coverage-gate requirement → enforced count.
# SUPPORTED sentences describe the languages the harness targets → total.

def count_rules(n_total: int, n_enforced: int):
    return [
        # gate-requirement phrasings → enforced (16)
        (re.compile(r"must exist for all (\d+) backends"), n_enforced, "gate"),
        (re.compile(r"(\d+) backends — a real port"), n_enforced, "gate"),
        # supported-languages phrasings → total (17, incl. deprecated Erlang)
        (re.compile(r"across (\d+) target language backends"), n_total, "supported"),
        (re.compile(r"(\d+) backends\. See the full table"), n_total, "supported"),
    ]


DOC_GLOBS = ["README.md", "docs/*.md"]


def iter_doc_files():
    for g in DOC_GLOBS:
        yield from sorted(REPO.glob(g))


# ── check / fix drivers ────────────────────────────────────────────────────

def run(fix: bool) -> int:
    backends = load_backends()
    n_total = len(backends)
    n_enforced = sum(1 for b in backends if b.enforced)
    problems: list[str] = []
    fixes: list[str] = []

    # 1. enforced ⊆ runner: every gate-enforced ext must be a real backend.
    runner_exts = {b.ext for b in backends}
    for ext in sorted(ENFORCED - runner_exts):
        problems.append(
            f"check_coverage.BACKENDS enforces '{ext}' but runner.sh has no "
            f"such backend — the gate and the dispatch disagree.")

    # 2. README table structural columns.
    readme = README.read_text()
    status = current_status_map(readme)
    expected_table = render_table(backends, status)
    m = re.search(r"## Supported Languages\s*\n+(\| Language \|.*?)(?=\n#|\Z)",
                  readme, re.DOTALL)
    current_table = m.group(1).rstrip() if m else ""
    if current_table.rstrip() != expected_table.rstrip():
        if fix:
            readme = replace_table(readme, expected_table)
            fixes.append("README.md: regenerated Supported Languages table")
        else:
            problems.append(
                "README.md Supported Languages table is stale "
                "(Extension/Target/rows/Deprecated flag drift from runner.sh). "
                "Run `python scripts/check_docs.py --fix`.")

    # 3. numeric count invariants across all docs.
    rules = count_rules(n_total, n_enforced)
    doc_text_cache: dict[Path, str] = {}
    if fix and readme != README.read_text():
        doc_text_cache[README] = readme  # carry the table fix forward
    for path in iter_doc_files():
        text = doc_text_cache.get(path, path.read_text())
        new_text = text
        for pat, expected, label in rules:
            for mm in pat.finditer(text):
                got = int(mm.group(1))
                if got != expected:
                    rel = path.relative_to(REPO)
                    if fix:
                        new_text = new_text.replace(mm.group(0),
                            mm.group(0).replace(mm.group(1), str(expected), 1))
                        fixes.append(f"{rel}: {label} count {got} → {expected}")
                    else:
                        problems.append(
                            f"{rel}: {label} count says {got}, expected "
                            f"{expected} — “{mm.group(0)}”.")
        if fix and new_text != text:
            doc_text_cache[path] = new_text

    if fix:
        for path, text in doc_text_cache.items():
            path.write_text(text)
        if fixes:
            print(f"Applied {len(fixes)} fix(es):")
            for f in fixes:
                print(f"  • {f}")
        else:
            print("Docs already in sync — nothing to fix.")
        # Re-run a verify pass so --fix is self-checking.
        return _verify_only(backends, n_total, n_enforced)

    if problems:
        print(f"FAIL: {len(problems)} doc-freshness problem(s):\n")
        for p in problems:
            print(f"  ✗ {p}")
        print("\nRun `python scripts/check_docs.py --fix` to update the docs.")
        return 1
    print(f"OK: docs in sync with code "
          f"({n_total} backends, {n_enforced} enforced by the gate).")
    return 0


def _verify_only(backends, n_total, n_enforced) -> int:
    """Post-fix verification (no writes)."""
    readme = README.read_text()
    status = current_status_map(readme)
    if render_table(backends, status).rstrip() not in readme:
        print("WARN: table still not matching after fix — inspect manually.")
        return 1
    for path in iter_doc_files():
        text = path.read_text()
        for pat, expected, _ in count_rules(n_total, n_enforced):
            for mm in pat.finditer(text):
                if int(mm.group(1)) != expected:
                    print(f"WARN: {path.relative_to(REPO)} still off after fix.")
                    return 1
    print("Verified: docs now in sync.")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Verify docs match the backend set.")
    ap.add_argument("--fix", action="store_true",
                    help="rewrite docs to match runner.sh / check_coverage.py")
    args = ap.parse_args(argv[1:])
    return run(args.fix)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
