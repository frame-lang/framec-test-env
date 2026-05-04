#!/usr/bin/env bash
# Phase 25 — RFC-0015 persist × multi-system fuzz runner.
# Transpiles each case and runs the dynamic-language ones in-process.

set -euo pipefail

cases_dir="$(dirname "$0")/cases_persist_multisys"
out_dir="${TMPDIR:-/tmp}/phase25_$$"
mkdir -p "$out_dir"

pass=0
fail=0
trans_fail=0

for case in "$cases_dir"/*; do
    name=$(basename "$case")
    lang=$(echo "$name" | sed 's/_p1_.*//')
    ext="${name##*.}"
    if ! framec compile -l "$lang" -o "$out_dir" "$case" 2>/dev/null; then
        echo "TRANSPILE FAIL: $name"
        trans_fail=$((trans_fail + 1))
        continue
    fi
    bare="$(basename "$case" ".$ext")"
    # `head -1` triggers SIGPIPE upstream once it exits. With
    # `pipefail` on, that propagates as failure even when the
    # command produced PASS first. Disable pipefail for the run.
    set +o pipefail
    case "$lang" in
        python_3)
            out=$(python3 "$out_dir/$bare.py" 2>&1 | head -1) || out="error"
            ;;
        javascript)
            # Frame's JS output uses ES-module `export` syntax;
            # Node treats `.js` as CommonJS unless package.json
            # opts in. Rename to `.mjs` before running.
            mv "$out_dir/$bare.js" "$out_dir/$bare.mjs"
            out=$(node "$out_dir/$bare.mjs" 2>/dev/null | head -1) || out="error"
            ;;
        typescript|rust)
            # ts-node + cargo serde_json need toolchain setup; the
            # matrix harness owns these. Transpile coverage above is
            # the smoke contract for this runner.
            set -o pipefail
            continue
            ;;
        *)
            set -o pipefail
            continue
            ;;
    esac
    set -o pipefail
    if [[ "$out" == PASS* ]]; then
        pass=$((pass + 1))
    else
        echo "RUN FAIL: $name → $out"
        fail=$((fail + 1))
    fi
done

echo "Summary: $pass passed, $fail run-failed, $trans_fail transpile-failed"
[[ $fail -eq 0 && $trans_fail -eq 0 ]]
