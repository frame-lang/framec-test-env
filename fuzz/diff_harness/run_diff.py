#!/usr/bin/env python3
"""Differential trace harness runner.

Takes a Frame source (the `@@system` block only — no harness), renders
it for every applicable backend via `langs.py`, compiles + runs, and
diffs every backend's TRACE: lines against the Python oracle.

Usage:
    run_diff.py path/to/source.frame [--langs python_3,javascript,...]

Exit code 0 if every backend's trace matches Python's; non-zero
otherwise (with a per-backend report on stdout).
"""
from __future__ import annotations
import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from langs import LANGS, Lang  # noqa: E402

FRAMEC = os.environ.get(
    "FRAMEC",
    str(Path(__file__).resolve().parents[3] / "framepiler" / "target" / "release" / "framec"),
)


@dataclass
class RunResult:
    lang: str
    stage: str               # "compile" | "run"
    ok: bool
    trace: list[str]
    stderr: str = ""


def build_source(lang: Lang, system_block: str) -> str:
    """Produce a Lang-specific source file from the Python-flavored
    canary `system_block`. Three transformations:
      1. Rewrite the `@@target` directive to this backend.
      2. Apply `lang.rewrite_trace` to the whole block (turns
         `print("TRACE: …")` into `console.log`, `println!`, etc.).
      3. Append `lang.render_canary` as the epilog harness."""
    lines = system_block.splitlines(keepends=True)
    rewritten = []
    prolog_injected = False
    for line in lines:
        if line.strip().startswith("@@target "):
            rewritten.append(f"@@target {lang.name}\n")
            if lang.prolog and not prolog_injected:
                rewritten.append("\n")
                rewritten.append(lang.prolog)
                if not lang.prolog.endswith("\n"):
                    rewritten.append("\n")
                prolog_injected = True
        else:
            rewritten.append(line)
    body = "".join(rewritten)
    body = lang.rewrite_trace(body)
    harness = lang.render_canary("") if lang.render_canary else ""
    return body + "\n" + harness


def run_one(lang: Lang, system_block: str, workdir: Path) -> RunResult:
    src = workdir / f"case.{lang.ext}"
    src.write_text(build_source(lang, system_block))

    out_dir = workdir / lang.name
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [FRAMEC, "compile", "-l", lang.name, "-o", str(out_dir), str(src)],
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return RunResult(
            lang.name, "compile", False, [],
            stderr=proc.stdout + proc.stderr,
        )

    # Find the emitted source file.
    candidates = [p for p in out_dir.iterdir() if p.suffix.lstrip(".") == lang.out_ext]
    if not candidates:
        return RunResult(
            lang.name, "compile", False, [],
            stderr=f"framec emitted no .{lang.out_ext} file",
        )
    emitted = candidates[0]

    # Optional compile step (Java javac, Rust rustc, etc.).
    if lang.compile:
        cc = lang.compile(emitted)
        proc = subprocess.run(cc, capture_output=True, text=True, cwd=out_dir)
        if proc.returncode != 0:
            return RunResult(
                lang.name, "compile", False, [],
                stderr=proc.stdout + proc.stderr,
            )

    # Run.
    run_cmd = lang.run(emitted) if lang.run else None
    if run_cmd is None:
        return RunResult(
            lang.name, "run", False, [],
            stderr=f"no run command configured for {lang.name}",
        )
    proc = subprocess.run(run_cmd, capture_output=True, text=True, timeout=30, cwd=out_dir)
    if proc.returncode != 0:
        return RunResult(
            lang.name, "run", False, [],
            stderr=proc.stdout + proc.stderr,
        )

    trace = [l for l in proc.stdout.splitlines() if l.startswith("TRACE: ")]
    return RunResult(lang.name, "run", True, trace, stderr="")


def run_all(system_block: str, wanted: list[str], workdir: Path) -> dict[str, RunResult]:
    results = {}
    for name in wanted:
        lang = LANGS.get(name)
        if lang is None:
            results[name] = RunResult(
                name, "config", False, [],
                stderr=f"no Lang config for {name}",
            )
            continue
        results[name] = run_one(lang, system_block, workdir)
    return results


def diff_against_oracle(results: dict[str, RunResult]) -> list[tuple[str, str]]:
    """Return (lang, reason) for every backend that disagrees with Python."""
    fails = []
    oracle = results.get("python_3")
    if oracle is None or not oracle.ok:
        fails.append(("python_3", oracle.stderr if oracle else "no oracle result"))
        return fails
    ref = oracle.trace
    for name, r in results.items():
        if name == "python_3":
            continue
        if not r.ok:
            fails.append((name, f"{r.stage} failed: {r.stderr[:200]}"))
            continue
        if r.trace != ref:
            diff = first_divergence(ref, r.trace)
            fails.append((name, diff))
    return fails


def first_divergence(a: list[str], b: list[str]) -> str:
    for i, (la, lb) in enumerate(zip(a, b)):
        if la != lb:
            return f"line {i+1}: oracle={la!r} got={lb!r}"
    if len(a) != len(b):
        return f"length: oracle={len(a)} got={len(b)}"
    return "identical"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path, help="Frame system block source")
    ap.add_argument("--langs", default=",".join(LANGS.keys()),
                    help="Comma-separated langs to run (default: all configured)")
    ap.add_argument("--workdir", type=Path,
                    default=Path("/tmp/diff_harness_work"))
    args = ap.parse_args()

    args.workdir.mkdir(parents=True, exist_ok=True)
    wanted = [l.strip() for l in args.langs.split(",") if l.strip()]

    system_block = args.source.read_text()
    results = run_all(system_block, wanted, args.workdir)

    # Report.
    print(f"=== Differential trace: {args.source.name} ===")
    for name in wanted:
        r = results.get(name)
        if r is None:
            print(f"  {name:12s}  MISSING")
            continue
        status = "OK " if r.ok else "FAIL"
        print(f"  {name:12s}  {status}  {len(r.trace)} trace lines")
        if not r.ok:
            for line in (r.stderr or "").splitlines()[:5]:
                print(f"    | {line}")

    fails = diff_against_oracle(results)
    if not fails:
        print("\nAll backends match Python oracle.")
        return 0
    print(f"\n{len(fails)} divergence(s):")
    for name, reason in fails:
        print(f"  {name:12s}  {reason}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
