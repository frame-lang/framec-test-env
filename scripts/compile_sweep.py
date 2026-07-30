#!/usr/bin/env python3
"""Compile-in-anger sweep — the correctness floor the byte-differential can't see.

`differential_test.sh` BYTE-compares ng's output to the 4.6.0.33 oracle, but it never COMPILES
ng's emitted code (its rust run-gate is literally `<run-skip:rust>`). So a fixture that differs by
five cosmetic bytes and a fixture that emits code that will not build read as the same "fail." This
sweep closes that gap: it emits every corpus fixture with ng and runs the target's real compiler,
then buckets the failures by error signature so you fix the dominant root-cause first.

  TARGET=rust   python3 scripts/compile_sweep.py           # proven; the reference target
  TARGET=python python3 scripts/compile_sweep.py           # py_compile syntax floor
  TARGET=c      python3 scripts/compile_sweep.py           # cc -c (compile, no link)
  TARGET=java   python3 scripts/compile_sweep.py           # javac (writes <Class>.java)

Why this matters for the languages beyond rust: ng emits ALL targets from ONE driver over one AST.
The bugs rust's sweep found (move-vs-clone / #186, wrong struct field names, dropped `static`
modifier, missing state-param hoist, dispatch-arm formatting, member visibility) are the driver's
decisions in per-language spellings — so a bug found in rust is a strong prior for the same bug in
python/java/c, and the byte-diff hides it there identically. Compile-FIRST, establish the floor,
then chase byte-identity on top of code that actually runs. See framec-cleanroom docs/JOURNAL.md
(2026-07-30) for the arc.

Caveats: external-crate fixtures (persist/async -> serde_json/tokio/serde) fail a bare compile but
compile in a cargo/deps project — they are NOT ng bugs; skim them out of the histogram. python uses
py_compile (SYNTAX only, not runtime); c compiles without linking (a `main` would need a link step).
"""
import os, re, glob, shutil, tempfile, subprocess, collections

TE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NG = os.environ.get("NG", "/Users/marktruluck/projects/framec-cleanroom/target/release/framec-ng")
TARGET = os.environ.get("TARGET", "rust")

# EXT      = the emitted-source file suffix (rs/py/java/c) for the on-disk file we compile.
# FIX_EXT  = the FIXTURE suffix. Each language has its OWN fixtures with ITS native main/stubs
#            (`.frs`/`.fpy`/`.fjava`/`.fc`). Compiling a rust `.frs` as java leaks the Rust `main`
#            in — always emit each target from ITS fixtures, or every fixture "fails" spuriously.
EXT = {"rust": "rs", "python": "py", "java": "java", "c": "c"}[TARGET]
FIX_EXT = {"rust": "frs", "python": "fpy", "java": "fjava", "c": "fc"}[TARGET]


def compile_cmd(src, td, code):
    if TARGET == "rust":
        return ["rustc", "--edition", "2021", "--crate-type", "bin", src, "-o", os.path.join(td, "out")]
    if TARGET == "python":
        return ["python3", "-m", "py_compile", src]
    if TARGET == "c":
        return ["cc", "-fsyntax-only", src]
    if TARGET == "java":
        return ["javac", "-d", td, src]  # src must already be named <PublicClass>.java (see below)
    raise SystemExit(f"unknown TARGET {TARGET}")


def java_class_name(code):
    m = re.search(r'\bpublic\s+(?:final\s+)?class\s+([A-Za-z_]\w*)', code) or \
        re.search(r'\bclass\s+([A-Za-z_]\w*)', code)
    return m.group(1) if m else None


def main():
    fixtures = sorted(glob.glob(f"{TE}/tests/common/positive/**/*.{FIX_EXT}", recursive=True))
    compiles = no_emit = 0
    fails = 0
    hist = collections.Counter()
    examples = collections.defaultdict(list)
    for f in fixtures:
        sub = os.path.relpath(f, f"{TE}/tests/common/positive")
        td = tempfile.mkdtemp()
        try:
            r = subprocess.run([NG, "-l", TARGET, "--emit", f], capture_output=True, text=True, timeout=30)
            code = r.stdout
            if not code.strip():
                no_emit += 1
                continue
            name = java_class_name(code) if TARGET == "java" else "m"
            if TARGET == "java" and not name:
                fails += 1; hist["(no-class)"] += 1; continue
            src = os.path.join(td, f"{name}.{EXT}")
            open(src, "w").write(code)
            rc = subprocess.run(compile_cmd(src, td, code), capture_output=True, text=True, timeout=60)
            if rc.returncode == 0:
                compiles += 1
            else:
                fails += 1
                codes = sorted(set(re.findall(r'error\[?(E\d{4})\]?', rc.stderr))) or ["(no-code)"]
                first = next((l[:150] for l in rc.stderr.splitlines() if l.strip() and
                              ("error" in l.lower())), "")
                for e in codes:
                    hist[e] += 1
                    if len(examples[e]) < 4:
                        examples[e].append(f"{sub}: {first}")
        except Exception as e:
            fails += 1; hist["(exception)"] += 1
        finally:
            shutil.rmtree(td, ignore_errors=True)
    print(f"TARGET={TARGET}  total={len(fixtures)} COMPILES={compiles} no_emit(ng)={no_emit} FAIL={fails}")
    print("=== error histogram (fix the dominant root-cause first) ===")
    for e, n in hist.most_common():
        print(f"  {e}  x{n}")
        for ex in examples[e][:3]:
            print(f"       {ex}")


if __name__ == "__main__":
    main()
