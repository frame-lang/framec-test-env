#!/usr/bin/env python3
"""Batch differential trace runner for Phase-2 @@persist fuzz.

Reads case/meta pairs from `cases/persist/`, renders the per-backend
epilog via `langs.py`'s `render_persist`, transpiles + compiles + runs,
and byte-diffs every backend's trace against the Python oracle.

Usage:
    run_persist.py                                  # all cases, all configured langs
    run_persist.py --max 20                         # first 20 cases
    run_persist.py --langs python_3,javascript       # subset of backends
    run_persist.py --cases ../cases/persist         # custom cases dir
"""
from __future__ import annotations
import argparse
import json
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
class CaseResult:
    case_id: str
    lang: str
    stage: str
    ok: bool
    trace: list[str]
    stderr: str = ""


def build_source(lang: Lang, system_block: str, meta: dict) -> str:
    """Produce lang-specific source: rewrite @@target, inject prolog,
    rewrite_trace, optionally append render_persist epilog.

    When the language uses a `run_persist_custom` hook (Erlang, …),
    the epilog lives in a separate driver file rather than being
    spliced into the Frame source, so `render_persist` isn't required."""
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
    # If the language has a `render_persist` callback, splice its
    # epilog into the Frame source (for backends where the driver
    # can live alongside the @@system block — all C-family langs,
    # Python, Ruby, GDScript, …). Otherwise the `run_persist_custom`
    # hook is solely responsible for building the driver (Erlang
    # escript pattern).
    if lang.render_persist is not None:
        harness = lang.render_persist(meta)
        return body + "\n" + harness
    if lang.run_persist_custom is None:
        raise RuntimeError(
            f"{lang.name}: neither render_persist nor run_persist_custom configured"
        )
    return body


def _docker_wrap(cmd: list[str], host_workdir: Path, image: str) -> list[str]:
    """Wrap `cmd` (an argv list expected to run inside `image`) with a
    `docker run --rm -v <host_workdir>:/work -w /work <image> <cmd>`
    invocation. The caller's command should reference paths under
    `/work` (the bind-mount's mount point)."""
    return [
        "docker", "run", "--rm",
        "-v", f"{host_workdir}:/work",
        "-w", "/work",
        "--entrypoint", cmd[0],
        image,
        *cmd[1:],
    ]


def run_one(lang: Lang, case_path: Path, meta: dict, workdir: Path) -> CaseResult:
    case_id = case_path.stem
    src_text = build_source(lang, case_path.read_text(), meta)

    case_dir = workdir / case_id / lang.name
    case_dir.mkdir(parents=True, exist_ok=True)
    src_file = case_dir / f"case.{lang.ext}"
    src_file.write_text(src_text)

    out_dir = case_dir / "out"
    out_dir.mkdir(exist_ok=True)
    proc = subprocess.run(
        [FRAMEC, "compile", "-l", lang.name, "-o", str(out_dir), str(src_file)],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        return CaseResult(case_id, lang.name, "transpile", False, [],
                          stderr=(proc.stdout + proc.stderr)[:500])

    candidates = [p for p in out_dir.iterdir() if p.suffix.lstrip(".") == lang.out_ext]
    if not candidates:
        return CaseResult(case_id, lang.name, "transpile", False, [],
                          stderr=f"framec emitted no .{lang.out_ext} file")
    emitted = candidates[0]

    # If the language supplies a custom runner (Erlang, GDScript, …),
    # bypass the standard compile+run flow.
    if lang.run_persist_custom is not None:
        stage, rc, output = lang.run_persist_custom(emitted, out_dir, meta)
        if rc != 0:
            return CaseResult(case_id, lang.name, stage, False, [],
                              stderr=output[:500])
        trace = [l for l in output.splitlines() if l.startswith("TRACE: ")]
        return CaseResult(case_id, lang.name, "run", True, trace)

    # For docker-backed langs, compile/run callables receive a path
    # rooted at `/work/<filename>` — the container's view of the bind
    # mount — rather than the host path.
    if lang.docker_image:
        path_for_cmd = Path("/work") / emitted.name
    else:
        path_for_cmd = emitted

    if lang.compile:
        cc = lang.compile(path_for_cmd)
        if lang.docker_image:
            cc = _docker_wrap(cc, out_dir, lang.docker_image)
        proc = subprocess.run(cc, capture_output=True, text=True, cwd=out_dir, timeout=180)
        if proc.returncode != 0:
            return CaseResult(case_id, lang.name, "compile", False, [],
                              stderr=(proc.stdout + proc.stderr)[:500])

    run_cmd = lang.run(path_for_cmd) if lang.run else None
    if run_cmd is None:
        return CaseResult(case_id, lang.name, "run", False, [],
                          stderr=f"no run command configured for {lang.name}")
    if lang.docker_image:
        run_cmd = _docker_wrap(run_cmd, out_dir, lang.docker_image)
    try:
        proc = subprocess.run(run_cmd, capture_output=True, text=True,
                              timeout=60, cwd=out_dir)
    except subprocess.TimeoutExpired:
        return CaseResult(case_id, lang.name, "run", False, [],
                          stderr="run timed out")
    if proc.returncode != 0:
        return CaseResult(case_id, lang.name, "run", False, [],
                          stderr=(proc.stdout + proc.stderr)[:500])

    trace = [l for l in proc.stdout.splitlines() if l.startswith("TRACE: ")]
    return CaseResult(case_id, lang.name, "run", True, trace)


def first_divergence(a: list[str], b: list[str]) -> str:
    for i, (la, lb) in enumerate(zip(a, b)):
        if la != lb:
            return f"line {i+1}: oracle={la!r} got={lb!r}"
    if len(a) != len(b):
        return f"length: oracle={len(a)} got={len(b)}"
    return "identical"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=Path,
                    default=Path(__file__).resolve().parents[1] / "cases" / "persist")
    ap.add_argument("--langs", default=None,
                    help="Comma-separated. Default: every backend with render_persist configured.")
    ap.add_argument("--max", type=int, default=None,
                    help="Limit to first N cases (by case_id sort).")
    ap.add_argument("--workdir", type=Path, default=Path("/tmp/persist_fuzz_work"))
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if args.langs:
        wanted = [l.strip() for l in args.langs.split(",") if l.strip()]
    else:
        # Include any backend that can run persist cases — either the
        # standard `render_persist` path or a `run_persist_custom` hook
        # (Erlang, GDScript — both covered).
        wanted = [
            k for k, v in LANGS.items()
            if v.render_persist is not None or v.run_persist_custom is not None
        ]
    if "python_3" not in wanted:
        print("FATAL: python_3 required as oracle", file=sys.stderr)
        return 2

    cases = sorted(args.cases.glob("case_*.frame"))
    if args.max:
        cases = cases[:args.max]
    if not cases:
        print(f"no cases found in {args.cases}", file=sys.stderr)
        return 2

    args.workdir.mkdir(parents=True, exist_ok=True)

    print(f"=== Phase 2 persist fuzz: {len(cases)} cases × {len(wanted)} backends ===")
    print(f"backends: {','.join(wanted)}")
    print()

    per_lang_stats: dict[str, dict[str, int]] = {
        lang: {"pass": 0, "transpile_fail": 0, "compile_fail": 0,
               "run_fail": 0, "diff_fail": 0}
        for lang in wanted
    }
    first_failures: dict[str, tuple[str, str]] = {}  # lang → (case_id, reason)

    for case_path in cases:
        case_id = case_path.stem
        meta_path = case_path.with_suffix(".meta")
        meta = json.loads(meta_path.read_text())

        # Oracle first.
        oracle = run_one(LANGS["python_3"], case_path, meta, args.workdir)
        if not oracle.ok:
            per_lang_stats["python_3"][oracle.stage + "_fail"] += 1
            if "python_3" not in first_failures:
                first_failures["python_3"] = (case_id, f"{oracle.stage}: {oracle.stderr[:200]}")
            # oracle failed → can't validate other backends on this case
            if args.verbose:
                print(f"  {case_id}  ORACLE FAIL ({oracle.stage})")
            continue
        per_lang_stats["python_3"]["pass"] += 1

        for lang_name in wanted:
            if lang_name == "python_3":
                continue
            result = run_one(LANGS[lang_name], case_path, meta, args.workdir)
            if not result.ok:
                per_lang_stats[lang_name][result.stage + "_fail"] += 1
                if lang_name not in first_failures:
                    first_failures[lang_name] = (
                        case_id, f"{result.stage}: {result.stderr[:200]}"
                    )
                if args.verbose:
                    print(f"  {case_id}  {lang_name:12s} {result.stage.upper()} FAIL")
                continue
            if result.trace != oracle.trace:
                per_lang_stats[lang_name]["diff_fail"] += 1
                if lang_name not in first_failures:
                    first_failures[lang_name] = (
                        case_id, first_divergence(oracle.trace, result.trace)
                    )
                if args.verbose:
                    print(f"  {case_id}  {lang_name:12s} DIFF")
                continue
            per_lang_stats[lang_name]["pass"] += 1

        if not args.verbose and (len([c for c in cases if cases.index(c) <= cases.index(case_path)]) % 20 == 0 or case_path == cases[-1]):
            # Progress dot every 20 cases.
            done = cases.index(case_path) + 1
            print(f"  ... {done}/{len(cases)}", flush=True)

    # Report
    print()
    print("=== Results ===")
    total_cases = len(cases)
    for lang in wanted:
        stats = per_lang_stats[lang]
        total = sum(stats.values())
        label = f"{lang}:"
        bits = [f"pass={stats['pass']}/{total_cases}"]
        for k in ("transpile_fail", "compile_fail", "run_fail", "diff_fail"):
            if stats[k]:
                bits.append(f"{k}={stats[k]}")
        print(f"  {label:15s} {' '.join(bits)}")
        if lang in first_failures:
            cid, reason = first_failures[lang]
            print(f"    first failure: {cid} — {reason}")

    any_failures = any(
        s != per_lang_stats[lang]["pass"]
        for lang, s in [(l, total_cases) for l in wanted]
    )
    return 1 if any_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
