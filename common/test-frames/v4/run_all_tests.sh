#!/bin/bash
# V4 Master Test Runner
# Runs all Frame V4 tests across the reorganized directory structure
#
# Directory structure:
#   common/<category>/  - Tests that pass in all 3 languages
#   python/<category>/  - Python-specific tests
#   typescript/<category>/ - TypeScript-specific tests
#   rust/<category>/    - Rust-specific tests

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEC="${FRAMEC:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"

# Test environment root (framepiler_test_env/)
TEST_ENV_ROOT="${FRAMEPILER_TEST_ENV:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"

# Language-specific output directories
PYTHON_OUT="${PYTHON_OUT:-$TEST_ENV_ROOT/python_test_crate/tests}"
TS_OUT="${TS_OUT:-$TEST_ENV_ROOT/typescript_test_crate/tests}"
RUST_CRATE="${RUST_CRATE:-$TEST_ENV_ROOT/rust_test_crate}"
RUST_OUT="$RUST_CRATE/tests"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# Counters
py_pass=0 py_fail=0
ts_pass=0 ts_fail=0
rs_pass=0 rs_fail=0

echo "=========================================="
echo "V4 Master Test Suite"
echo "=========================================="
echo "Using framec: $FRAMEC"
echo ""

# Run the core PRT tests (common/primary/)
if [ -x "$SCRIPT_DIR/common/primary/run_tests.sh" ]; then
    echo ">>> Running core PRT tests..."
    "$SCRIPT_DIR/common/primary/run_tests.sh"
    echo ""
fi

# Function to run a single test
run_test() {
    local test_file="$1"
    local lang="$2"

    local test_name=$(basename "$test_file" | sed 's/\.f[a-z]*$//')

    case $lang in
        python_3) out_dir="$PYTHON_OUT"; out_ext="py" ;;
        typescript) out_dir="$TS_OUT"; out_ext="ts" ;;
        rust) out_dir="$RUST_OUT"; out_ext="rs" ;;
    esac

    local out_file="$out_dir/${test_name}.${out_ext}"

    # Compile
    if ! "$FRAMEC" compile -l "$lang" -o "$out_dir" "$test_file" 2>/dev/null; then
        return 1
    fi

    # Run
    case $lang in
        python_3)
            output=$(python3 "$out_file" 2>&1)
            ;;
        typescript)
            output=$(cd "$TEST_ENV_ROOT/typescript_test_crate" && npx ts-node "tests/${test_name}.ts" 2>&1)
            ;;
        rust)
            output=$(cd "$RUST_CRATE" && cargo run --bin "$test_name" 2>&1)
            ;;
    esac

    if echo "$output" | grep -q "PASS"; then
        return 0
    else
        return 1
    fi
}

# Run common tests (all 3 languages)
echo ">>> Running common category tests..."
for category in operators scoping validator core control_flow data_types capabilities exec_smoke interfaces systems; do
    category_dir="$SCRIPT_DIR/common/$category"
    if [ -d "$category_dir" ] && [ "$(ls -A $category_dir 2>/dev/null)" ]; then
        echo "  Category: $category"

        # Get unique test names from .fpy files
        for fpy in "$category_dir"/*.fpy; do
            [ -f "$fpy" ] || continue
            test_name=$(basename "$fpy" .fpy)

            # Python
            if run_test "$fpy" python_3; then
                echo -e "    $test_name [py:${GREEN}OK${NC}]"
                py_pass=$((py_pass + 1))
            else
                echo -e "    $test_name [py:${RED}FAIL${NC}]"
                py_fail=$((py_fail + 1))
            fi

            # TypeScript
            fts="${fpy%.fpy}.fts"
            if [ -f "$fts" ]; then
                if run_test "$fts" typescript; then
                    ts_pass=$((ts_pass + 1))
                else
                    ts_fail=$((ts_fail + 1))
                fi
            fi

            # Rust
            frs="${fpy%.fpy}.frs"
            if [ -f "$frs" ]; then
                if run_test "$frs" rust; then
                    rs_pass=$((rs_pass + 1))
                else
                    rs_fail=$((rs_fail + 1))
                fi
            fi
        done
    fi
done

# Run Python-specific tests
echo ""
echo ">>> Running Python-specific tests..."
for category in async capabilities control_flow core data_types interfaces systems; do
    category_dir="$SCRIPT_DIR/python/$category"
    if [ -d "$category_dir" ] && [ "$(ls -A $category_dir 2>/dev/null)" ]; then
        for fpy in "$category_dir"/*.fpy ; do
            [ -f "$fpy" ] || continue
            test_name=$(basename "$fpy" .fpy)
            if run_test "$fpy" python_3; then
                echo -e "  $test_name [py:${GREEN}OK${NC}]"
                py_pass=$((py_pass + 1))
            else
                echo -e "  $test_name [py:${RED}FAIL${NC}]"
                py_fail=$((py_fail + 1))
            fi
        done
    fi
done

# Run TypeScript-specific tests
echo ""
echo ">>> Running TypeScript-specific tests..."
for category in imports control_flow core systems; do
    category_dir="$SCRIPT_DIR/typescript/$category"
    if [ -d "$category_dir" ] && [ "$(ls -A $category_dir 2>/dev/null)" ]; then
        for fts in "$category_dir"/*.fts ; do
            [ -f "$fts" ] || continue
            test_name=$(basename "$fts" .fts)
            if run_test "$fts" typescript; then
                echo -e "  $test_name [ts:${GREEN}OK${NC}]"
                ts_pass=$((ts_pass + 1))
            else
                echo -e "  $test_name [ts:${RED}FAIL${NC}]"
                ts_fail=$((ts_fail + 1))
            fi
        done
    fi
done

# Run Rust-specific tests
echo ""
echo ">>> Running Rust-specific tests..."
for category in control_flow core known_issues; do
    category_dir="$SCRIPT_DIR/rust/$category"
    if [ -d "$category_dir" ] && [ "$(ls -A $category_dir 2>/dev/null)" ]; then
        for frs in "$category_dir"/*.frs ; do
            [ -f "$frs" ] || continue
            test_name=$(basename "$frs" .frs)
            if run_test "$frs" rust; then
                echo -e "  $test_name [rs:${GREEN}OK${NC}]"
                rs_pass=$((rs_pass + 1))
            else
                echo -e "  $test_name [rs:${RED}FAIL${NC}]"
                rs_fail=$((rs_fail + 1))
            fi
        done
    fi
done

# Summary
echo ""
echo "=========================================="
echo "Summary (excluding PRT core tests)"
echo "=========================================="
echo -e "Python:     ${GREEN}$py_pass passed${NC}, ${RED}$py_fail failed${NC}"
echo -e "TypeScript: ${GREEN}$ts_pass passed${NC}, ${RED}$ts_fail failed${NC}"
echo -e "Rust:       ${GREEN}$rs_pass passed${NC}, ${RED}$rs_fail failed${NC}"
echo ""

total_fail=$((py_fail + ts_fail + rs_fail))
if [ $total_fail -gt 0 ]; then
    exit 1
fi
