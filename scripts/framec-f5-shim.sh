#!/usr/bin/env bash
# f5 adapter — presents the `-l <target> --emit <file>` CLI that `golden_run.py`
# drives, on top of f5. Sibling of `framec-ng-shim.sh` and
# `framec-oracle-shim.sh`: one harness, many compilers, selected by `NG=`.
#
# WHY THIS EXISTS. f5's own `tools/conformance.sh` compares the two compilers'
# EXIT CODES and nothing else. That cannot see the defect class measured on
# 2026-08-25: a compiler that accepts a program, emits code the host compiles,
# and returns the WRONG VALUE (f5 #298, #296). `golden_run.py` runs the four
# stages that answer the question exit codes cannot --
#
#     emit -> build -> RUN -> assert TAP
#
# -- and its header records that everything downstream of `emit()` is already
# compiler-agnostic: it only ever sees a file on disk. So the whole cost of
# putting f5 under that gate is translating one CLI into another, which is this
# file. The test env is not modified by a single byte; `NG=` selects the
# compiler and it may live anywhere.
#
#   NG=tools/f5-goldenrun-shim.sh python3 scripts/golden_run.py rust --all
#
# THE CALLING CONVENTION, from golden_run.py's `emit()`:
#     [NG, "-l", <target>, "--emit", <fixture>]   -> emission on STDOUT, exit 0
# A non-zero exit OR empty stdout is recorded as a stage-1 failure, which is the
# correct reading of an f5 refusal.
#
# F5 BINARY: override with F5=/path/to/f5 (default = this checkout's release build).
set -uo pipefail
F5=${F5:-$HOME/projects/f5/target/release/f5}
[ -x "$F5" ] || { echo "framec-f5-shim: no f5 binary at $F5 -- override with F5=/path/to/f5 (build: ./tools/build.sh in the f5 checkout)" >&2; exit 3; }

target=""; fixture=""
while [ $# -gt 0 ]; do
    case "$1" in
        -l|--language) target="${2:-}"; shift 2 ;;
        --emit)        shift ;;          # f5 emits to stdout by default
        -*)            shift ;;          # ignore flags f5 does not take
        *)             fixture="$1"; shift ;;
    esac
done
[ -n "$fixture" ] || { echo "framec-f5-shim: no input file" >&2; exit 2; }

# THE TARGET NAMES DIFFER AND THE MISMATCH IS SILENT. golden_run.py says
# `python`; f5 says `python_3`. Passing the wrong one through would make f5
# refuse with E007 and the harness would record a stage-1 failure -- a shim bug
# wearing a compiler bug's clothes, which is the failure f5 #110 already cost a
# day to. Anything not mapped here is REFUSED rather than guessed.
case "$target" in
    rust)    t=rust ;;
    python)  t=python_3 ;;
    go)      t=go ;;
    typescript) t=typescript ;;
    java)    t=java ;;
    c|cpp|csharp|lua|swift|kotlin|dart|php|ruby|gdscript|javascript|erlang)
        echo "framec-f5-shim: f5 has no '$target' arm -- refusing rather than guessing" >&2
        exit 2 ;;
    "")      echo "framec-f5-shim: no -l <target> given" >&2; exit 2 ;;
    *)       echo "framec-f5-shim: unknown target '$target'" >&2; exit 2 ;;
esac

# Diagnostics to stderr, emission to stdout -- which is already f5's shape, so
# this is a pass-through. The exit status is f5's own (65 on refusal).
exec "$F5" --language "$t" "$fixture"
