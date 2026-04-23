#!/bin/bash
# Compile-Error Test Runner — TAP format output.
#
# Each test is a Frame source containing deliberately bad NATIVE syntax
# (not bad Frame syntax). The contract being locked in: framec must
# pass native code through verbatim — no silent rewriting of literals,
# types, or expressions to paper over an author mistake. The target
# compiler catches the error.
#
# A test PASSES if:
#   1. framec transpiles cleanly (framec owns Frame syntax, not native)
#   2. the target language compiler REJECTS the emitted code.
#
# A test FAILS if:
#   - framec fails to transpile (Frame-level regression), OR
#   - the target compiler accepts the bad native syntax, meaning framec
#     silently "fixed" it (passthrough-contract regression).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

FRAMEC="${FRAMEC:-$REPO_ROOT/framepiler/target/release/framec}"
if [ ! -x "$FRAMEC" ]; then
    echo "Bail out! framec not found at $FRAMEC — set FRAMEC env var"
    exit 1
fi

WORK=$(mktemp -d "${TMPDIR:-/tmp}/compile-error.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

PASS=0
FAIL=0
SKIP=0
TEST_NUM=0

echo "TAP version 13"

# Check commands for each target language. A test passes if AT LEAST
# ONE of these rejects the emitted code:
#   - compile: pure syntax check (parse only; cheap, reliable)
#   - runtime: execute the file (catches semantic errors like NameError
#     that syntactic parsers accept)
# Interpreted languages return both lists; compiled languages just
# the compile list. Separated so the runner reports WHICH stage
# caught the error.
compile_cmds_for() {
    local ext="$1"
    local path="$2"
    case "$ext" in
        fc)   echo "gcc -fsyntax-only -x c $path" ;;
        fpy)  echo "python3 -m py_compile $path" ;;
        fjs)  echo "node --check $path" ;;
        fts)  echo "npx --no-install tsc --noEmit --target es2020 --module esnext $path" ;;
        frs)  echo "rustc --edition=2021 --emit=metadata -o /dev/null $path" ;;
        flua) echo "luac -p $path" ;;
        ferl) echo "erlc -Wno-warn-unused-vars $path" ;;
        fphp) echo "php -l $path" ;;
        frb)  echo "ruby -c $path" ;;
        *) echo "" ;;
    esac
}
runtime_cmds_for() {
    # Only for languages where running the file is cheap and safe
    # (dynamic languages that otherwise need actual execution to
    # surface NameError / TypeError / badmatch).
    local ext="$1"
    local path="$2"
    case "$ext" in
        fpy)  echo "python3 $path" ;;
        fjs)  echo "node $path" ;;
        fphp) echo "php $path" ;;
        flua) echo "lua5.4 $path" ;;
        frb)  echo "ruby $path" ;;
        *) echo "" ;;
    esac
}

run_compile_error_test() {
    local src="$1"
    local name="$(basename "$src")"
    local ext="${src##*.}"
    TEST_NUM=$((TEST_NUM + 1))

    local out_dir="$WORK/case_$TEST_NUM"
    mkdir -p "$out_dir"
    local stem="$(basename "$src" .$ext)"

    # Map Frame ext → target language & emitted filename
    local target out_file
    case "$ext" in
        fc)   target="c";   out_file="$out_dir/$stem.c"   ;;
        fpy)  target="python"; out_file="$out_dir/$stem.py" ;;
        fjs)  target="javascript"; out_file="$out_dir/$stem.js" ;;
        fts)  target="typescript"; out_file="$out_dir/$stem.ts" ;;
        frs)  target="rust"; out_file="$out_dir/$stem.rs" ;;
        flua) target="lua";  out_file="$out_dir/$stem.lua" ;;
        ferl) target="erlang"; out_file="$out_dir/$stem.erl" ;;
        fphp) target="php";  out_file="$out_dir/$stem.php" ;;
        frb)  target="ruby"; out_file="$out_dir/$stem.rb" ;;
        *)
            echo "ok $TEST_NUM - $name # SKIP unknown extension"
            SKIP=$((SKIP + 1))
            return
            ;;
    esac

    # 1. Transpile — must succeed.
    local framec_err
    framec_err=$("$FRAMEC" compile -l "$target" -o "$out_dir" "$src" 2>&1) || {
        echo "not ok $TEST_NUM - $name # framec refused (Frame-level regression)"
        echo "  ---"
        echo "  framec-output: |"
        echo "$framec_err" | sed 's/^/    /'
        echo "  ..."
        FAIL=$((FAIL + 1))
        return
    }

    if [ ! -s "$out_file" ]; then
        echo "not ok $TEST_NUM - $name # framec succeeded but produced no output at $out_file"
        FAIL=$((FAIL + 1))
        return
    fi

    # 2. Target compile — SHOULD fail. If compile accepts it, try
    #    runtime execution (catches NameError/TypeError in dynamic
    #    languages). Test passes if EITHER rejects.
    local ccmd rcmd
    ccmd=$(compile_cmds_for "$ext" "$out_file")
    rcmd=$(runtime_cmds_for "$ext" "$out_file")
    if [ -z "$ccmd" ] && [ -z "$rcmd" ]; then
        echo "ok $TEST_NUM - $name # SKIP no check command for .$ext"
        SKIP=$((SKIP + 1))
        return
    fi

    local stage=""
    if [ -n "$ccmd" ]; then
        if ! $ccmd >/dev/null 2>&1; then
            stage="compile"
        fi
    fi
    if [ -z "$stage" ] && [ -n "$rcmd" ]; then
        if ! $rcmd >/dev/null 2>&1; then
            stage="runtime"
        fi
    fi

    if [ -n "$stage" ]; then
        echo "ok $TEST_NUM - $name ($target) # correctly rejected at $stage"
        PASS=$((PASS + 1))
    else
        echo "not ok $TEST_NUM - $name ($target) # UNEXPECTED: both compile and runtime accepted"
        echo "  ---"
        echo "  message: framec passthrough may have silently rewritten the bad native syntax."
        echo "  ..."
        FAIL=$((FAIL + 1))
    fi
}

# Run all tests — stable order by name.
for src in $(ls "$SCRIPT_DIR"/*.fc "$SCRIPT_DIR"/*.fpy "$SCRIPT_DIR"/*.fjs \
                "$SCRIPT_DIR"/*.fts "$SCRIPT_DIR"/*.frs "$SCRIPT_DIR"/*.flua \
                "$SCRIPT_DIR"/*.ferl "$SCRIPT_DIR"/*.fphp "$SCRIPT_DIR"/*.frb \
                2>/dev/null | sort); do
    [ -f "$src" ] || continue
    run_compile_error_test "$src"
done

echo "1..$TEST_NUM"
echo ""
echo "# Compile-error tests: $PASS passed, $FAIL failed, $SKIP skipped"

[ $FAIL -eq 0 ]
