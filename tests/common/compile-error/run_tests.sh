#!/bin/bash
# Compile-Error Test Runner - TAP format output
# Tests that certain Frame constructs transpile OK but FAIL to compile
# (Frame passes through invalid native syntax that the target compiler rejects)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEC="${FRAMEC:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"
TMPDIR="${TMPDIR:-/tmp}"

# Colors (disabled if not tty)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
fi

# Counters
PASS=0
FAIL=0
SKIP=0
TEST_NUM=0

# Output TAP header
echo "TAP version 13"

# Helper: run compile-error test
# Args: $1=source_file
run_compile_error_test() {
    local src="$1"
    local name="$(basename "$src")"
    local ext="${src##*.}"

    TEST_NUM=$((TEST_NUM + 1))

    # Determine target language and compiler
    case "$ext" in
        fc)
            local target="c"
            local out="$TMPDIR/neg_test_$$.c"
            local compile_cmd="gcc -fsyntax-only $out"
            ;;
        fpy)
            local target="python"
            local out="$TMPDIR/neg_test_$$.py"
            local compile_cmd="python3 -m py_compile $out"
            ;;
        fts)
            local target="typescript"
            local out="$TMPDIR/neg_test_$$.ts"
            local compile_cmd="npx tsc --noEmit $out"
            ;;
        frs)
            local target="rust"
            local out="$TMPDIR/neg_test_$$.rs"
            local compile_cmd="rustc --emit=metadata -o /dev/null $out"
            ;;
        *)
            echo "ok $TEST_NUM - $name # SKIP unknown extension"
            SKIP=$((SKIP + 1))
            return
            ;;
    esac

    # Transpile
    if ! "$FRAMEC" "$src" > "$out" 2>&1; then
        echo "not ok $TEST_NUM - $name # transpilation failed"
        FAIL=$((FAIL + 1))
        rm -f "$out"
        return
    fi

    # Compile - SHOULD FAIL for negative tests
    if $compile_cmd 2>/dev/null; then
        echo "not ok $TEST_NUM - $name ($target) # UNEXPECTED: compiled successfully"
        echo "  ---"
        echo "  message: Expected compilation to fail, but it succeeded"
        echo "  severity: fail"
        echo "  ..."
        FAIL=$((FAIL + 1))
    else
        echo "ok $TEST_NUM - $name ($target) # correctly rejected by $target compiler"
        PASS=$((PASS + 1))
    fi

    rm -f "$out"
}

# Find and run all negative tests
for src in "$SCRIPT_DIR"/*.fc "$SCRIPT_DIR"/*.fpy "$SCRIPT_DIR"/*.fts "$SCRIPT_DIR"/*.frs; do
    [ -f "$src" ] || continue
    run_compile_error_test "$src"
done

# TAP plan (at end for streaming)
echo "1..$TEST_NUM"
echo ""

# Summary
echo "# Compile-error tests: $PASS passed, $FAIL failed, $SKIP skipped"

if [ $FAIL -gt 0 ]; then
    exit 1
fi
