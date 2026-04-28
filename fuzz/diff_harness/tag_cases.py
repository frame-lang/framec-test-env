#!/usr/bin/env python3
"""Retro-tag existing fuzz case .meta files for the unified runner
contract (TAG_VOCABULARY.md, TEST_INFRA_ROADMAP.md).

Walks each phase's cases directory and adds a `tags` list to every
case's .meta file. Tags are derived from the case's `harness_kind`
+ `axes` so retro-tagging is deterministic and idempotent.

Tier assignment:
- smoke: simple axes only (smallest state-count / no HSM / single
  domain type / etc.) — ~50 cases per phase.
- core: smoke + cases that historically surfaced bugs, marked via
  per-phase rules below.
- full: every case.

Usage:
    tag_cases.py                          # tag all phases
    tag_cases.py --phase persist          # one phase
    tag_cases.py --dry-run                # show what would change
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KINDS = ("persist", "selfcall", "hsm", "operations", "async", "multisys")


def derive_tags(meta: dict) -> list[str]:
    """Derive the tag list for one case from its .meta."""
    kind = meta.get("harness_kind", "")
    axes = meta.get("axes", {})
    tags: list[str] = []

    # Per-phase feature tag.
    if kind == "persist":
        tags.append("persist")
        tags.append("save-restore")
    elif kind == "selfcall":
        tags.append("selfcall")
    elif kind == "hsm":
        tags.append("hsm")
    elif kind == "operations":
        tags.append("operations")
    elif kind == "async":
        tags.append("async")
    elif kind in ("multi_system", "multisys"):
        tags.append("multisys")
    else:
        # Unknown kind — preserve case but no feature tag.
        return tags

    # Common axis tags.
    if "n_states" in axes:
        tags.append(f"n-states-{axes['n_states']}")
    if "hsm_depth" in axes:
        d = axes["hsm_depth"]
        tags.append(f"hsm-{d}")
        # Old vocab: "depth-N" used loosely. Map hsm_depth to hsm-N
        # only; depth-N is reserved for expression nesting.
    if "domain_set" in axes:
        tags.append(f"domain-{axes['domain_set']}")
    if "target_offset" in axes:
        tags.append(f"target-offset-{axes['target_offset']}")

    # Phase-specific axes.
    if kind == "selfcall":
        if "post_structure" in axes:
            tags.append(axes["post_structure"])  # linear / if_guarded / if_both_arms
        if "post_call_stmts" in axes:
            tags.append(f"post-stmts-{axes['post_call_stmts']}")
    elif kind == "hsm":
        if "parent_action" in axes:
            tags.append(axes["parent_action"])  # parent / sibling / uncle
        if "post_forward_structure" in axes:
            tags.append(axes["post_forward_structure"])  # linear / if_guarded / if_both_arms
        if "post_forward_stmts" in axes:
            tags.append(f"post-stmts-{axes['post_forward_stmts']}")
        if "child_pre_stmts" in axes:
            tags.append(f"child-pre-{axes['child_pre_stmts']}")
    elif kind == "operations":
        if "caller_context" in axes:
            tags.append(f"caller-{axes['caller_context']}")
        if "return_type" in axes:
            tags.append(f"return-{axes['return_type']}")
        if "domain_access" in axes:
            tags.append(f"domain-{axes['domain_access']}")
    elif kind == "async":
        if "pattern" in axes:
            tags.append(f"pattern-{axes['pattern']}")
    elif kind in ("multisys", "multi_system"):
        if "pattern" in axes:
            tags.append(f"pattern-{axes['pattern']}")

    return tags


def derive_tier(meta: dict, tags: list[str]) -> str:
    """Pick the tier (smoke / core / full) for one case.

    smoke: smallest axis combination per phase. Captures one
      representative per major axis category.
    core: smoke + per-phase bug-finding patterns (when known).
    full: everything else.
    """
    kind = meta.get("harness_kind", "")
    axes = meta.get("axes", {})

    # Default-conservative: full unless explicitly smoke/core.
    if kind == "persist":
        # Smoke: 2-state, flat HSM, int-only domain, target_offset=0.
        if (axes.get("n_states") == 2
                and axes.get("hsm_depth") == 0
                and axes.get("domain_set") == "int"
                and axes.get("target_offset") == 0):
            return "smoke"
        # Core: 2-state and 3-state with hsm_depth ≤ 1 (the cases
        # that surfaced framec bugs during bring-up).
        if (axes.get("n_states") in (2, 3)
                and axes.get("hsm_depth", 0) <= 1):
            return "core"
        return "full"
    elif kind == "selfcall":
        # Smoke: linear post-structure, n_states=2, hsm_depth=0.
        if (axes.get("post_structure") == "linear"
                and axes.get("n_states") == 2
                and axes.get("hsm_depth") == 0):
            return "smoke"
        # Core: linear only.
        if axes.get("post_structure") == "linear":
            return "core"
        return "full"
    elif kind == "hsm":
        # Smoke: parent_action ∈ {parent, sibling}, simplest post-
        # forward (linear, 0 child_pre_stmts).
        if (axes.get("parent_action") in ("parent", "sibling")
                and axes.get("post_forward_structure") == "linear"
                and axes.get("child_pre_stmts", 0) == 0):
            return "smoke"
        # Core: parent / sibling actions (any post-forward shape).
        if axes.get("parent_action") in ("parent", "sibling"):
            return "core"
        return "full"
    elif kind == "operations":
        # Smoke: interface caller, int return, no domain access
        # (the simplest representative — one per caller_context).
        if (axes.get("caller_context") == "interface"
                and axes.get("return_type") == "int"
                and axes.get("domain_access") == "none"):
            return "smoke"
        # Core: interface caller (any return / domain).
        if axes.get("caller_context") == "interface":
            return "core"
        return "full"
    elif kind == "async":
        # Smoke: single_await pattern, 2-state, flat.
        pat = axes.get("pattern", "")
        if (pat == "single_await"
                and axes.get("n_states") == 2
                and axes.get("hsm_depth") == 0):
            return "smoke"
        # Core: single_await or two_phase_init (≤2 awaits worth).
        if pat in ("single_await", "two_phase_init"):
            return "core"
        return "full"
    elif kind in ("multisys", "multi_system"):
        # Smoke: simplest pattern (multi_call covers most), 2-state, flat.
        pat = axes.get("pattern", "")
        if (pat == "multi_call"
                and axes.get("n_states") == 2
                and axes.get("hsm_depth") == 0):
            return "smoke"
        # Core: any common pattern.
        if pat in ("multi_call", "simple_call"):
            return "core"
        return "full"
    return "full"


def tag_one_case(meta_path: Path, dry_run: bool = False) -> bool:
    """Tag one case. Returns True if .meta changed."""
    try:
        meta = json.loads(meta_path.read_text())
    except Exception as e:
        print(f"  skip {meta_path.name}: malformed meta ({e})")
        return False

    # Idempotency: derive tags fresh each call. Preserves any user-
    # added tags not in the derived set ("manual:" prefix convention).
    derived = derive_tags(meta)
    tier = derive_tier(meta, derived)
    if tier not in derived:
        derived.append(tier)

    existing = meta.get("tags", [])
    manual_tags = [t for t in existing if t.startswith("manual:")]
    new_tags = sorted(set(derived) | set(manual_tags))

    if existing == new_tags:
        return False

    meta["tags"] = new_tags
    if not dry_run:
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    return True


def tag_phase(kind: str, dry_run: bool = False) -> tuple[int, int]:
    cases_dir = REPO_ROOT / "cases" / kind
    if not cases_dir.is_dir():
        print(f"phase {kind}: no cases dir ({cases_dir}) — skipping")
        return (0, 0)
    metas = sorted(cases_dir.glob("case_*.meta"))
    n_changed = 0
    for m in metas:
        if tag_one_case(m, dry_run=dry_run):
            n_changed += 1
    print(f"phase {kind}: {n_changed} / {len(metas)} cases retagged"
          f"{' (dry run)' if dry_run else ''}")
    return (n_changed, len(metas))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default=None,
                    help="One phase kind (persist/selfcall/hsm/operations/async/multisys). "
                         "Default: all phases.")
    ap.add_argument("--dry-run", action="store_true",
                    help="Compute tags but don't write .meta files.")
    args = ap.parse_args()

    kinds = (args.phase,) if args.phase else DEFAULT_KINDS
    total_changed = 0
    total_seen = 0
    for k in kinds:
        c, s = tag_phase(k, dry_run=args.dry_run)
        total_changed += c
        total_seen += s
    print(f"=== total: {total_changed} / {total_seen} retagged ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
