#!/usr/bin/env python3
"""
Batch-generate `<stem>.f<ext>.skip.md` files for fixtures that are
intentionally not ported to certain backends.

Each batch entry is a dict:
  - stem_path  : path under tests/common/positive (e.g.
                 "primary/52_hsm_state_arg_propagation")
  - real_exts  : list of backends with real ports (e.g. ["frs"])
  - title      : short markdown H1 for the skip.md
  - body       : markdown body explaining why this fixture is
                 intentionally skipped on the other backends

The 16 missing backends each get an identical `<stem>.<ext>.skip.md`
file. The skip text is uniform — the reason is "this fixture is
target-specific by design", not per-backend.

Run: scripts/gen_skipmd.py
Reads the BATCHES list at the bottom of this file. Idempotent: skips
any `.skip.md` that already exists.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POSITIVE_DIR = REPO_ROOT / "tests" / "common" / "positive"

ALL_BACKENDS: tuple[str, ...] = (
    "fc", "fcpp", "fcs", "fdart", "ferl", "fgd", "fgo", "fjava",
    "fjs", "fkt", "flua", "fphp", "fpy", "frb", "frs", "fswift", "fts",
)


@dataclass
class SkipBatch:
    stem_path: str       # e.g. "primary/52_hsm_state_arg_propagation"
    real_exts: list[str]  # backends that have real ports, e.g. ["frs"]
    title: str
    body: str


def render_skip_md(batch: SkipBatch) -> str:
    return f"# {batch.title}\n\n{batch.body.rstrip()}\n"


def run(batches: list[SkipBatch]) -> int:
    total_created = 0
    total_existed = 0
    for batch in batches:
        content = render_skip_md(batch)
        for ext in ALL_BACKENDS:
            if ext in batch.real_exts:
                continue
            target = POSITIVE_DIR / f"{batch.stem_path}.{ext}.skip.md"
            if target.exists():
                total_existed += 1
                continue
            target.write_text(content)
            total_created += 1
        print(f"  {batch.stem_path}: {len(ALL_BACKENDS) - len(batch.real_exts)} backends")
    print()
    print(f"Created: {total_created}   Already existed (idempotent skip): {total_existed}")
    return 0


# ---------------------------------------------------------------------------
# Batches — one entry per single-target fixture in framework dirs (not
# cookbook dirs scientific/security/robotics/parser_specialists, which
# belong to the cookbook port agent).
# ---------------------------------------------------------------------------

BATCHES: list[SkipBatch] = [
    # === primary/ audit-verified single-target fixtures ===
    SkipBatch(
        stem_path="primary/52_hsm_state_arg_propagation",
        real_exts=["frs"],
        title="Intentional skip — Rust-only regression net",
        body=(
            "This fixture is a Rust-only regression net for the D5 "
            "cascade-visibility fix. The bug it guards against was "
            "specific to Rust's compartment-mutation path; other "
            "backends had different cascade behavior and aren't "
            "covered by the same regression.\n\n"
            "See `docs/partial-coverage-audit.md` for the audit "
            "entry."
        ),
    ),
    SkipBatch(
        stem_path="primary/55_nested_frame_args",
        real_exts=["fpy"],
        title="Intentional skip — Python-only smoke fixture",
        body=(
            "Python-only smoke fixture for nested `@@SystemName($(arg))` "
            "call resolution. No regression coverage value on other "
            "backends since the codegen path is target-agnostic.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),
    SkipBatch(
        stem_path="primary/99_persist_param_child",
        real_exts=["fgd"],
        title="Intentional skip — GDScript-specific regression",
        body=(
            "GDScript-only regression for the parameterized-child × "
            "domain-init fix (`#328` in framec memory). The bug was "
            "GDScript-codegen-specific; other backends already "
            "handled the case correctly.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),
    SkipBatch(
        stem_path="primary/106_hsm_3deep_cascade",
        real_exts=["fpy"],
        title="Intentional skip — Python-only RFC-0019 smoke",
        body=(
            "Python smoke fixture covering 3-deep HSM cascade per "
            "RFC-0019 (`#408` in framec memory). Same cascade "
            "behavior is exercised across all 17 backends by the "
            "matrix's broader HSM tests (tests 46, 47, 48, 49, 53, "
            "61, 62 etc.).\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),

    # === interfaces/ audit-verified single-target ===
    SkipBatch(
        stem_path="interfaces/return_typed",
        real_exts=["fts"],
        title="Intentional skip — TypeScript-specific edge case",
        body=(
            "TypeScript-only fixture for a TS-parser quirk in typed "
            "return-value handling. Not a feature test — a "
            "regression net for one specific TS codegen path.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),

    # === capabilities/ audit-verified single-target ===
    SkipBatch(
        stem_path="capabilities/nested_functions",
        real_exts=["fc"],
        title="Intentional skip — C-only test",
        body=(
            "C-only test for nested-function handling in native "
            "prolog. C is the only target where the issue surfaces; "
            "other backends handle nested helper functions via their "
            "native scoping rules without Frame-side intervention.\n\n"
            "See `docs/partial-coverage-audit.md`."
        ),
    ),
]


if __name__ == "__main__":
    sys.exit(run(BATCHES))
