#!/bin/bash
# Transpile-Error Test Runner - TAP format output
# Tests that certain invalid Frame constructs are REJECTED by the transpiler
# (Transpiler should fail with an error message)

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

# Helper: run transpile-error test
# Args: $1=source_file
run_transpile_error_test() {
    local src="$1"
    local name="$(basename "$src")"
    local out="$TMPDIR/transpile_err_test_$$.out"

    TEST_NUM=$((TEST_NUM + 1))

    # Transpile - SHOULD FAIL for transpile-error tests
    if "$FRAMEC" "$src" > "$out" 2>&1; then
        echo "not ok $TEST_NUM - $name # UNEXPECTED: transpilation succeeded"
        echo "  ---"
        echo "  message: Expected transpilation to fail, but it succeeded"
        echo "  severity: fail"
        echo "  ..."
        FAIL=$((FAIL + 1))
    else
        echo "ok $TEST_NUM - $name # correctly rejected by transpiler"
        PASS=$((PASS + 1))
    fi

    rm -f "$out"
}

# Find and run all transpile-error tests
for src in "$SCRIPT_DIR"/*.fc "$SCRIPT_DIR"/*.fpy "$SCRIPT_DIR"/*.fts "$SCRIPT_DIR"/*.frs; do
    [ -f "$src" ] || continue
    run_transpile_error_test "$src"
done

# TAP plan (at end for streaming)
echo "1..$TEST_NUM"
echo ""

# Summary
echo "# Transpile-error tests: $PASS passed, $FAIL failed, $SKIP skipped"

if [ $FAIL -gt 0 ]; then
    exit 1
fi
