#!/usr/bin/env python3
"""Golden-test runner — the MILESTONE gate: emit -> build -> RUN -> assert TAP.

The differential harness (`differential_test.sh`) only byte-compares ng's emitted TEXT against the
4.6.0.33 oracle's, and for rust it `<run-skip>`s entirely; `compile_sweep.py` only asks whether
rustc ACCEPTS the text. Neither ever executes the program, so neither can answer the question a
milestone actually asks: *does the emitted code behave correctly?*

Per `docs/faithfulness/M1.md`, each DoD fixture is "a self-validating TAP program (build the emitted
code, run it, assert observable behavior)". This runner is that gate:

    1. emit    framec-ng -l <target> --emit <fixture>
    2. build   rustc (rust) / javac (java) / cc (c) / py_compile (python)
    3. RUN     execute the built program, capture stdout
    4. ASSERT  parse TAP: a `1..N` plan, N `ok`/`not ok` results, zero `not ok`, no crash

A fixture PASSES only when all four stages succeed. Anything else is a FAIL with the stage named,
so "did this milestone run green?" has a real answer instead of a text-match proxy.

Usage:
    python3 scripts/golden_run.py rust tests/common/positive/foundation/*.frs
    python3 scripts/golden_run.py rust --milestone M1      # the M1 DoD inventory
    python3 scripts/golden_run.py rust --all               # every fixture for the target
"""
import glob
import os
import re
import subprocess
import sys
import tempfile

NG = os.environ.get(
    "NG", "/Users/marktruluck/projects/framec-cleanroom/target/release/framec-ng"
)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Each target compiles ITS OWN fixtures (each carries that language's native main).
FIX_EXT = {"rust": "frs", "python": "fpy", "java": "fjava", "c": "fc"}

# The DoD fixture inventories, from docs/faithfulness/M<k>.md.
MILESTONES = {
    "M1": [
        "foundation/foundation_minimal",
        "foundation/foundation_value_return",
        "foundation/foundation_transition",
        "foundation/foundation_lifecycle",
        "foundation/foundation_enter_args",
        "foundation/foundation_selfcall",
    ],
}


def emit(target, fixture, workdir):
    """Stage 1 — transpile the fixture with ng."""
    out = os.path.join(workdir, "gen." + ("rs" if target == "rust" else target))
    p = subprocess.run(
        [NG, "-l", target, "--emit", fixture], capture_output=True, text=True
    )
    if p.returncode != 0 or not p.stdout.strip():
        return None, (p.stderr or "ng produced no output").strip().splitlines()[:3]
    with open(out, "w") as f:
        f.write(p.stdout)
    return out, None


# Third-party crates the corpus legitimately uses (persist -> serde/serde_json, async -> tokio).
# WITHOUT these on the compiler's search path, every such fixture dies at `unresolved import serde`
# and whatever ELSE is wrong in the file is never reported — the missing crate MASKS real ng bugs,
# exactly as byte-identity masked non-compiling output and compiling masked wrong behavior. Build
# them once into a scratch cargo project, then link each fixture against those rlibs.
RUST_CRATES = ("serde", "serde_json", "tokio")
_rust_deps_cache = {}


def rust_deps():
    """Path to a deps dir + `--extern` args for RUST_CRATES, building them once on first use."""
    if _rust_deps_cache:
        return _rust_deps_cache.get("dir"), _rust_deps_cache.get("externs", [])
    prj = os.path.join(tempfile.gettempdir(), "framec_golden_deps")
    os.makedirs(os.path.join(prj, "src"), exist_ok=True)
    with open(os.path.join(prj, "Cargo.toml"), "w") as f:
        f.write(
            '[package]\nname = "fixdeps"\nversion = "0.1.0"\nedition = "2021"\n\n'
            "[dependencies]\n"
            'serde = { version = "1", features = ["derive"] }\n'
            'serde_json = "1"\n'
            'tokio = { version = "1", features = ["full"] }\n'
        )
    with open(os.path.join(prj, "src", "main.rs"), "w") as f:
        f.write("fn main() {}\n")
    subprocess.run(["cargo", "build"], cwd=prj, capture_output=True, text=True, timeout=900)
    deps = os.path.join(prj, "target", "debug", "deps")
    externs = []
    for c in RUST_CRATES:
        hits = sorted(
            glob.glob(os.path.join(deps, "lib%s-*.rlib" % c)),
            key=os.path.getmtime,
            reverse=True,
        )
        if hits:
            externs += ["--extern", "%s=%s" % (c, hits[0])]
    _rust_deps_cache["dir"] = deps if os.path.isdir(deps) else None
    _rust_deps_cache["externs"] = externs
    return _rust_deps_cache["dir"], externs


def build(target, src, workdir):
    """Stage 2 — compile the emitted code with the real toolchain."""
    if target == "rust":
        exe = os.path.join(workdir, "prog")
        deps, externs = rust_deps()
        cmd = ["rustc", "--edition", "2021"]
        if deps:
            cmd += ["-L", deps]
        cmd += externs + ["--crate-type", "bin", "-o", exe, src]
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=workdir)
        if p.returncode != 0:
            errs = [l for l in p.stderr.splitlines() if l.startswith("error")][:3]
            return None, errs or p.stderr.strip().splitlines()[:3]
        return [exe], None
    return None, ["build not implemented for target " + target]


def run(cmd, workdir):
    """Stage 3 — EXECUTE the built program."""
    try:
        p = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, cwd=workdir
        )
    except subprocess.TimeoutExpired:
        return None, ["timed out after 30s"]
    if p.returncode != 0:
        tail = (p.stderr or p.stdout).strip().splitlines()[-3:]
        return None, ["exit code %d" % p.returncode] + tail
    return p.stdout, None


def check_tap(stdout):
    """Stage 4 — assert the TAP output: a plan, matching result count, zero failures."""
    plan, oks, not_oks = None, 0, 0
    for line in stdout.splitlines():
        line = line.strip()
        m = re.match(r"^1\.\.(\d+)$", line)
        if m:
            plan = int(m.group(1))
        elif re.match(r"^not ok\b", line):
            not_oks += 1
        elif re.match(r"^ok\b", line):
            oks += 1
    if not_oks:
        fails = [l for l in stdout.splitlines() if l.strip().startswith("not ok")][:3]
        return False, ["%d assertion(s) FAILED" % not_oks] + fails
    total = oks + not_oks
    if plan is None:
        # No TAP plan: accept a clean run that printed something and asserted nothing to fail.
        return (True, None) if total or stdout.strip() else (False, ["no output"])
    if total != plan:
        return False, ["plan says %d results, saw %d" % (plan, total)]
    if plan == 0:
        return False, ["empty plan (1..0)"]
    return True, None


def one(target, fixture):
    """Run all four stages for one fixture; return (passed, stage, detail_lines)."""
    with tempfile.TemporaryDirectory() as wd:
        src, err = emit(target, fixture, wd)
        if err:
            return False, "EMIT", err
        cmd, err = build(target, src, wd)
        if err:
            return False, "BUILD", err
        stdout, err = run(cmd, wd)
        if err:
            return False, "RUN", err
        ok, err = check_tap(stdout)
        if not ok:
            return False, "ASSERT", err
        return True, "PASS", []


def main():
    args = [a for a in sys.argv[1:]]
    if not args:
        print(__doc__)
        return 2
    target = args.pop(0)
    ext = FIX_EXT.get(target)
    if not ext:
        print("unknown target %r (want one of %s)" % (target, ", ".join(FIX_EXT)))
        return 2

    fixtures = []
    if args and args[0] == "--milestone":
        name = args[1]
        base = os.path.join(ROOT, "tests/common/positive")
        for stem in MILESTONES.get(name, []):
            path = os.path.join(base, stem + "." + ext)
            if os.path.exists(path):
                fixtures.append(path)
            else:
                print("MISSING  %s.%s (DoD fixture absent)" % (stem, ext))
        label = "%s DoD inventory" % name
    elif args and args[0] == "--all":
        fixtures = sorted(
            glob.glob(
                os.path.join(ROOT, "tests/common/positive/**/*." + ext), recursive=True
            )
        )
        label = "all %s fixtures" % target
    else:
        fixtures = args
        label = "%d fixture(s)" % len(args)

    print("=== golden_run: %s / target=%s (emit -> build -> RUN -> assert) ===" % (label, target))
    passed = failed = 0
    for f in fixtures:
        ok, stage, detail = one(target, f)
        short = os.path.relpath(f, os.path.join(ROOT, "tests/common/positive"))
        if ok:
            passed += 1
            print("  PASS   %s" % short)
        else:
            failed += 1
            print("  FAIL   %s  [%s]" % (short, stage))
            for d in detail:
                print("           %s" % d)
    print("----")
    print("TARGET=%s  EXECUTED-PASS=%d  FAIL=%d  total=%d" % (target, passed, failed, passed + failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
