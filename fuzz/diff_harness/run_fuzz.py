#!/usr/bin/env python3
"""Batch differential trace runner for the pure-Frame fuzz harness.

Reads `case_NNNN.frame` + `.meta` pairs from a cases directory,
dispatches to the per-backend renderer keyed on `meta["harness_kind"]`
(persist, selfcall, hsm, operations, async, multi_system, …),
transpiles + compiles + runs each case under every configured
backend, and byte-diffs every backend's trace against the Python
oracle.

Backends register per-kind renderers in `langs.py`'s
`Lang.renderers: dict[str, Callable[[dict], str]]`. Some backends
(Erlang, GDScript) instead supply a `run_custom` hook that
bypasses the standard compile+run flow.

Usage:
    run_fuzz.py                                   # default cases dir (../cases/persist), all backends
    run_fuzz.py --cases ../cases/selfcall         # Phase-3 @@:self fuzz
    run_fuzz.py --max 20                          # first 20 cases
    run_fuzz.py --langs python_3,javascript       # subset of backends
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import threading
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
    stage: str  # "transpile" | "compile" | "run" | "skip"
    ok: bool
    trace: list[str]
    stderr: str = ""
    # Distinct from ok=False: the backend explicitly doesn't support
    # this case's axis combination (see `Lang.case_supported`).
    skipped: bool = False


def build_source(lang: Lang, system_block: str, meta: dict) -> str:
    """Produce lang-specific source: rewrite @@target, inject prolog,
    rewrite_trace, optionally append a kind-specific renderer's epilog.

    The renderer is looked up in `lang.renderers` via
    `meta["harness_kind"]`. When the language's only hook is
    `run_custom` (Erlang, …) the epilog is emitted separately by
    that hook rather than spliced into the Frame source here."""
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
    # Default kind is "persist" for back-compat with legacy meta files
    # that predate the harness_kind field.
    kind = meta.get("harness_kind", "persist")
    renderer = lang.renderers.get(kind)
    if renderer is not None:
        harness = renderer(meta)
        return body + "\n" + harness
    # Backends without an in-source renderer for this kind must supply
    # `run_custom` (Erlang escript, GDScript godot invocation).
    if lang.run_custom is None:
        raise RuntimeError(
            f"{lang.name}: no renderers[{kind!r}] or run_custom configured"
        )
    return body


# ─── Persistent-container pool for docker-backed backends ────────────
#
# Previously each `_docker_wrap` invocation fired `docker run --rm …`,
# starting a fresh container per case per stage (compile + run).
# For Phase-2 at 81 cases × ~6 docker backends × 2 stages = ~1000
# container cold starts (≈ 0.5-2 s each) that's minutes of overhead
# before a single test runs.
#
# The new model: bring up ONE container per backend at fuzz start,
# bind-mount the whole fuzz workdir at `/fuzz_work`, sleep it as
# `pid 1`, and run each case via `docker exec` into that same
# container. A single `docker rm -f` tears down at the end (registered
# via atexit so we clean up on Ctrl-C too).
#
# The containers themselves are named `fuzz-<lang>` so parallel runs
# in separate workdirs can be distinguished; on collision we reuse.

_POOL_CONTAINERS: dict[str, str] = {}  # lang_name → container_id
_POOL_WORKDIR: Optional[Path] = None
_POOL_LOCK = threading.Lock()  # guards _POOL_CONTAINERS mutations

# Per-backend semaphores enforce `Lang.concurrency_limit`. Only
# populated for langs that set the field (memory-heavy toolchains
# like kotlinc with -J-Xmx2g). Built lazily in `_get_backend_sem`.
_BACKEND_SEMAPHORES: dict[str, threading.Semaphore] = {}
_BACKEND_SEM_LOCK = threading.Lock()


def _get_backend_sem(lang: Lang) -> Optional[threading.Semaphore]:
    """Return the shared semaphore for this backend, or None if the
    backend has no concurrency cap. Lazy-inits under a lock so the
    first race resolves to a single Semaphore instance."""
    if lang.concurrency_limit is None:
        return None
    sem = _BACKEND_SEMAPHORES.get(lang.name)
    if sem is not None:
        return sem
    with _BACKEND_SEM_LOCK:
        sem = _BACKEND_SEMAPHORES.get(lang.name)
        if sem is None:
            sem = threading.Semaphore(lang.concurrency_limit)
            _BACKEND_SEMAPHORES[lang.name] = sem
        return sem


def _container_name(lang_name: str, workdir: Path) -> str:
    # Include a short workdir hash so two fuzz runs in different
    # workdirs don't collide on the same container name.
    import hashlib
    wd_hash = hashlib.sha1(str(workdir).encode()).hexdigest()[:8]
    return f"fuzz-{lang_name}-{wd_hash}"


def _ensure_pool(lang: Lang, workdir: Path) -> str:
    """Start (or reuse) a long-running container for `lang.docker_image`
    bind-mounting `workdir` at `/fuzz_work`. Returns the container
    name; subsequent `docker exec` calls use it.

    Thread-safe: guarded by `_POOL_LOCK` so concurrent callers for
    the same lang race through a single container-start."""
    # Fast path: already started.
    cached = _POOL_CONTAINERS.get(lang.name)
    if cached is not None:
        return cached
    with _POOL_LOCK:
        # Re-check under the lock — another thread may have started
        # the container while we were waiting.
        cached = _POOL_CONTAINERS.get(lang.name)
        if cached is not None:
            return cached
        assert lang.docker_image is not None
        name = _container_name(lang.name, workdir)
        # Remove any stale container with this name (e.g. previous run
        # interrupted before atexit fired).
        subprocess.run(["docker", "rm", "-f", name],
                       capture_output=True, check=False)
        proc = subprocess.run(
            [
                "docker", "run", "-d", "--name", name,
                "-v", f"{workdir}:/fuzz_work",
                "--entrypoint", "sleep",
                lang.docker_image,
                "infinity",
            ],
            capture_output=True, text=True, timeout=60,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"docker run -d failed for {lang.docker_image}: "
                f"{(proc.stderr or proc.stdout).strip()}"
            )
        _POOL_CONTAINERS[lang.name] = name
        return name


def _teardown_pool() -> None:
    """Tear down all persistent fuzz containers. Registered via
    atexit so interrupted runs don't leak containers. Parallelized
    via raw threads — `ThreadPoolExecutor` can't accept new submits
    after interpreter shutdown, and serial teardown of 6-7
    containers would add 20-30 s to the tail of every fuzz run."""
    names = list(_POOL_CONTAINERS.values())
    if not names:
        return
    threads: list[threading.Thread] = []
    for n in names:
        t = threading.Thread(
            target=lambda name=n: subprocess.run(
                ["docker", "rm", "-f", name],
                capture_output=True, check=False,
            ),
            daemon=False,
        )
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    _POOL_CONTAINERS.clear()


import atexit
atexit.register(_teardown_pool)


def _docker_wrap(cmd: list[str], host_workdir: Path, lang: Lang,
                 fuzz_workdir: Path) -> list[str]:
    """Wrap `cmd` (an argv list expected to run inside `lang`'s
    container) as a `docker exec` into the persistent per-lang
    container. The caller's command should reference paths under
    `/work` (the case's output dir, mounted indirectly under
    `/fuzz_work/<case_id>/<lang>/out/`).

    `host_workdir` is the case's output directory on the host; we
    map that to the container's `/work` via the fuzz-wide bind mount
    at `/fuzz_work`."""
    container = _ensure_pool(lang, fuzz_workdir)
    # Translate host path → container path via /fuzz_work prefix.
    try:
        rel = host_workdir.relative_to(fuzz_workdir)
    except ValueError:
        raise RuntimeError(
            f"host workdir {host_workdir} not under fuzz workdir {fuzz_workdir}"
        )
    container_wd = f"/fuzz_work/{rel}"
    return [
        "docker", "exec",
        "-w", container_wd,
        container,
        *cmd,
    ]


def run_one(lang: Lang, case_path: Path, meta: dict, workdir: Path) -> CaseResult:
    # Honor per-backend case filter — some backends can't express
    # certain axis values (e.g. Erlang's if/case syntax differs
    # structurally from C-family if-else).
    if lang.case_supported is not None and not lang.case_supported(meta):
        return CaseResult(
            case_path.stem, lang.name, "skip", True, [], skipped=True,
        )
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

    # Acquire the per-backend concurrency cap, if one is set. The
    # semaphore is a no-op (returns None, `with` block is a pass) for
    # backends without a cap. Gates only the downstream compile+run
    # steps — the `framec` transpile above is cheap and shared.
    backend_sem = _get_backend_sem(lang)
    if backend_sem is not None:
        backend_sem.acquire()
    try:
        return _run_one_toolchain(lang, case_id, emitted, out_dir, meta, workdir)
    finally:
        if backend_sem is not None:
            backend_sem.release()


def _run_one_toolchain(lang: Lang, case_id: str, emitted: Path,
                       out_dir: Path, meta: dict, workdir: Path) -> CaseResult:
    """Compile + run phase of run_one, extracted so the per-backend
    semaphore wrapper in run_one can own the acquire/release."""
    # If the language supplies a custom runner (Erlang, GDScript, …),
    # bypass the standard compile+run flow.
    if lang.run_custom is not None:
        # Build the per-case context: the fuzz workdir plus a closure
        # that wraps a cmd as `docker exec` into the persistent
        # container. Custom hooks use this instead of firing their
        # own `docker run --rm` per case.
        def _docker_exec_in(cmd: list[str], host_cwd: Path) -> list[str]:
            return _docker_wrap(cmd, host_cwd, lang, workdir)
        ctx = {"fuzz_workdir": workdir, "docker_exec": _docker_exec_in}
        stage, rc, output = lang.run_custom(emitted, out_dir, meta, ctx)
        if rc != 0:
            return CaseResult(case_id, lang.name, stage, False, [],
                              stderr=output[:500])
        trace = [l for l in output.splitlines() if l.startswith("TRACE: ")]
        return CaseResult(case_id, lang.name, "run", True, trace)

    # For docker-backed langs, compile/run callables receive the
    # bare emitted filename — the persistent container is exec'd with
    # `-w` set to the case's output directory (via the fuzz-wide
    # `/fuzz_work` bind mount), so relative paths resolve correctly
    # inside the container. Historically we passed `/work/<name>`;
    # the pool's cwd-based model is cleaner.
    if lang.docker_image:
        path_for_cmd = Path(emitted.name)
    else:
        path_for_cmd = emitted

    if lang.compile:
        cc = lang.compile(path_for_cmd)
        if lang.docker_image:
            cc = _docker_wrap(cc, out_dir, lang, workdir)
        proc = subprocess.run(cc, capture_output=True, text=True, cwd=out_dir, timeout=180)
        if proc.returncode != 0:
            return CaseResult(case_id, lang.name, "compile", False, [],
                              stderr=(proc.stdout + proc.stderr)[:500])

    run_cmd = lang.run(path_for_cmd) if lang.run else None
    if run_cmd is None:
        return CaseResult(case_id, lang.name, "run", False, [],
                          stderr=f"no run command configured for {lang.name}")
    if lang.docker_image:
        run_cmd = _docker_wrap(run_cmd, out_dir, lang, workdir)
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
    import os as _os
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", type=Path,
                    default=Path(__file__).resolve().parents[1] / "cases" / "persist")
    ap.add_argument("--langs", default=None,
                    help="Comma-separated. Default: every backend that can run this kind.")
    ap.add_argument("--max", type=int, default=None,
                    help="Limit to first N cases (by case_id sort).")
    ap.add_argument("--workdir", type=Path, default=Path("/tmp/fuzz_work"))
    ap.add_argument(
        "--jobs", "-j", type=int,
        default=max(4, (_os.cpu_count() or 4)),
        help="Parallel case workers (default: CPU count, min 4). "
             "Each worker processes one case's full pipeline "
             "(transpile → compile → run → diff) end-to-end; docker "
             "backends serialize on the shared persistent container, "
             "which handles concurrent `docker exec` calls safely.",
    )
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    # Peek at the first case's meta to discover which kind we're
    # running; this lets `--langs` default filter by backends that can
    # render THAT specific kind rather than by whether they have any
    # renderer at all.
    cases_sorted = sorted(args.cases.glob("case_*.frame"))
    first_kind = "persist"
    if cases_sorted:
        try:
            first_kind = json.loads(
                cases_sorted[0].with_suffix(".meta").read_text()
            ).get("harness_kind", "persist")
        except Exception:
            pass

    if args.langs:
        wanted = [l.strip() for l in args.langs.split(",") if l.strip()]
    else:
        wanted = [
            k for k, v in LANGS.items()
            if v.renderers.get(first_kind) is not None or v.run_custom is not None
        ]
    if "python_3" not in wanted:
        print("FATAL: python_3 required as oracle", file=sys.stderr)
        return 2

    cases = cases_sorted
    if args.max:
        cases = cases[:args.max]
    if not cases:
        print(f"no cases found in {args.cases}", file=sys.stderr)
        return 2

    args.workdir.mkdir(parents=True, exist_ok=True)

    print(f"=== {first_kind} fuzz: {len(cases)} cases × {len(wanted)} backends ===")
    print(f"backends: {','.join(wanted)}")
    print()

    per_lang_stats: dict[str, dict[str, int]] = {
        lang: {"pass": 0, "skip": 0, "transpile_fail": 0, "compile_fail": 0,
               "run_fail": 0, "diff_fail": 0}
        for lang in wanted
    }
    first_failures: dict[str, tuple[str, str]] = {}  # lang → (case_id, reason)
    stats_lock = threading.Lock()

    def process_case(case_path: Path) -> None:
        """Full pipeline for one case: oracle → other backends → diff.
        Thread-safe against `per_lang_stats` / `first_failures` via
        `stats_lock`. Safe against other concurrent cases because each
        case has its own output directory."""
        case_id = case_path.stem
        meta = json.loads(case_path.with_suffix(".meta").read_text())

        oracle = run_one(LANGS["python_3"], case_path, meta, args.workdir)
        with stats_lock:
            if oracle.skipped:
                per_lang_stats["python_3"]["skip"] += 1
                return
            if not oracle.ok:
                per_lang_stats["python_3"][oracle.stage + "_fail"] += 1
                first_failures.setdefault(
                    "python_3",
                    (case_id, f"{oracle.stage}: {oracle.stderr[:200]}"),
                )
                return
            per_lang_stats["python_3"]["pass"] += 1

        for lang_name in wanted:
            if lang_name == "python_3":
                continue
            result = run_one(LANGS[lang_name], case_path, meta, args.workdir)
            with stats_lock:
                if result.skipped:
                    per_lang_stats[lang_name]["skip"] += 1
                    continue
                if not result.ok:
                    per_lang_stats[lang_name][result.stage + "_fail"] += 1
                    first_failures.setdefault(
                        lang_name,
                        (case_id, f"{result.stage}: {result.stderr[:200]}"),
                    )
                    continue
                if result.trace != oracle.trace:
                    per_lang_stats[lang_name]["diff_fail"] += 1
                    first_failures.setdefault(
                        lang_name,
                        (case_id, first_divergence(oracle.trace, result.trace)),
                    )
                    continue
                per_lang_stats[lang_name]["pass"] += 1

    # Pre-warm the docker container pool so startup happens once rather
    # than racing between threads. Each docker-backed lang gets its
    # container spun up serially here before the parallel work starts.
    for lang_name in wanted:
        lang = LANGS[lang_name]
        if lang.docker_image is not None:
            _ensure_pool(lang, args.workdir)

    # Dispatch all cases to a thread pool. Each worker runs one case's
    # full pipeline end-to-end. Inside a case, the oracle runs first,
    # then the other backends sequentially — that's just the case's
    # local data dependency, not a cross-case serialization.
    from concurrent.futures import ThreadPoolExecutor, as_completed
    done_count = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(process_case, cp) for cp in cases]
        for fut in as_completed(futures):
            fut.result()  # surface exceptions
            done_count += 1
            if not args.verbose and (
                done_count % 20 == 0 or done_count == len(cases)
            ):
                print(f"  ... {done_count}/{len(cases)}", flush=True)

    # Report
    print()
    print("=== Results ===")
    total_cases = len(cases)
    any_failures = False
    for lang in wanted:
        stats = per_lang_stats[lang]
        applicable = total_cases - stats["skip"]
        label = f"{lang}:"
        bits = [f"pass={stats['pass']}/{applicable}"]
        if stats["skip"]:
            bits.append(f"skip={stats['skip']}")
        for k in ("transpile_fail", "compile_fail", "run_fail", "diff_fail"):
            if stats[k]:
                bits.append(f"{k}={stats[k]}")
                any_failures = True
        print(f"  {label:15s} {' '.join(bits)}")
        if lang in first_failures:
            cid, reason = first_failures[lang]
            print(f"    first failure: {cid} — {reason}")

    return 1 if any_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
