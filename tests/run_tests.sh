#!/bin/bash
#
# Frame V4 Unified Test Runner
# ============================
#
# Dynamically discovers and runs all Frame V4 tests.
# See README.md for full documentation.
#
# USAGE:
#   ./run_tests.sh                    # Run all tests (parallel by default)
#   ./run_tests.sh --serial           # Run all tests sequentially
#   ./run_tests.sh --python           # Run only Python tests
#   ./run_tests.sh --langs py,ts,rs   # Run only specified languages
#   ./run_tests.sh --category primary # Run only primary category
#   ./run_tests.sh --help             # Show help
#
# DIRECTORY CONVENTION:
#   common/positive/<category>/   - Positive tests (transpile OK, compile OK, run OK)
#   common/compile-error/         - Compile-error tests (transpile OK, compile fails)
#   common/transpile-error/       - Transpile-error tests (transpiler rejects)
#   common/runtime-error/         - Runtime-error tests (transpile OK, compile OK, run fails)
#   python/<category>/            - Python-only tests (.fpy)
#   typescript/<category>/        - TypeScript-only tests (.fts)
#   rust/<category>/              - Rust-only tests (.frs)
#   c/<category>/                 - C-only tests (.fc)
#
# FILE MARKERS (in first 10 lines of test file):
#   // @@skip              - Skip this test
#   // @@xfail             - Expected to fail (runs, counts as failure)
#   // @@timeout <seconds> - Custom timeout (default: 30)
#

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEC="${FRAMEC:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"

# Ensure all tool directories are in PATH (non-login shells like CI / Claude Code
# don't source the user's profile, so tools from homebrew, cargo, nvm, etc.
# aren't on PATH). This is the ONE place to fix it — both this script and
# run_single_test.sh (spawned by xargs -P) inherit this PATH.
for __dir in "$HOME/.cargo/bin" "/usr/local/bin" "/opt/homebrew/bin"; do
    if [ -d "$__dir" ]; then
        case ":$PATH:" in
            *":$__dir:"*) ;;  # already present
            *) export PATH="$__dir:$PATH" ;;
        esac
    fi
done
unset __dir

# Test environment root
TEST_ENV_ROOT="${FRAMEPILER_TEST_ENV:-$(cd "$SCRIPT_DIR/.." && pwd)}"

# Output directories
PYTHON_OUT="$TEST_ENV_ROOT/output/python/tests"
TS_OUT="$TEST_ENV_ROOT/output/typescript/tests"
RUST_CRATE="$TEST_ENV_ROOT/output/rust"
RUST_OUT="$RUST_CRATE/tests"
C_OUT="$TEST_ENV_ROOT/output/c/tests"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters (bash 3.2 compatible - no associative arrays)
python_pass=0 python_fail=0 python_skip=0 python_known=0
typescript_pass=0 typescript_fail=0 typescript_skip=0 typescript_known=0
rust_pass=0 rust_fail=0 rust_skip=0 rust_known=0
c_pass=0 c_fail=0 c_skip=0 c_known=0

# Command line options
FILTER_LANG=""
FILTER_LANGS=""
FILTER_CATEGORY=""
VERBOSE=false
COMPILE_ONLY=false
PARALLEL=true  # Parallel is now the default
JOBS=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --python|--py) FILTER_LANG="python" ;;
        --typescript|--ts) FILTER_LANG="typescript" ;;
        --rust|--rs) FILTER_LANG="rust" ;;
        --c) FILTER_LANG="c" ;;
        --langs|-l)
            # Parse comma-separated language list (py,ts,rs,c -> python typescript rust c)
            FILTER_LANGS=""
            IFS=',' read -ra LANG_PARTS <<< "$2"
            for part in "${LANG_PARTS[@]}"; do
                case "$part" in
                    py|python) FILTER_LANGS="$FILTER_LANGS python" ;;
                    ts|typescript) FILTER_LANGS="$FILTER_LANGS typescript" ;;
                    rs|rust) FILTER_LANGS="$FILTER_LANGS rust" ;;
                    c) FILTER_LANGS="$FILTER_LANGS c" ;;
                    *) echo "Unknown language: $part"; exit 1 ;;
                esac
            done
            FILTER_LANGS=$(echo "$FILTER_LANGS" | xargs)  # Trim whitespace
            shift
            ;;
        --category|-c) FILTER_CATEGORY="$2"; shift ;;
        --verbose|-v) VERBOSE=true ;;
        --compile-only) COMPILE_ONLY=true ;;
        --serial|-s) PARALLEL=false ;;
        --parallel|-p) PARALLEL=true ;;
        --jobs|-j) JOBS="$2"; shift ;;
        --help|-h)
            echo "Frame V4 Test Runner"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --python, --py      Run only Python tests"
            echo "  --typescript, --ts  Run only TypeScript tests"
            echo "  --rust, --rs        Run only Rust tests"
            echo "  --c                 Run only C tests"
            echo "  --langs, -l LANGS   Run specified languages (comma-separated: py,ts,rs,c)"
            echo "  --category, -c NAME Run only tests in category NAME"
            echo "  --verbose, -v       Show detailed output"
            echo "  --compile-only      Only compile, don't run"
            echo "  --serial, -s        Run tests sequentially (default: parallel)"
            echo "  --parallel, -p      Run tests in parallel (default)"
            echo "  --jobs, -j N        Number of parallel jobs (default: $JOBS)"
            echo "  --help, -h          Show this help"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

# Create output directories
mkdir -p "$PYTHON_OUT" "$TS_OUT" "$RUST_OUT" "$C_OUT"

# Temp directory for parallel results
RESULTS_DIR=$(mktemp -d)
trap "rm -rf $RESULTS_DIR" EXIT

# Language to framec target
lang_to_target() {
    case $1 in
        python) echo "python_3" ;;
        typescript) echo "typescript" ;;
        rust) echo "rust" ;;
        c) echo "c" ;;
    esac
}

# Language to output directory
lang_to_outdir() {
    case $1 in
        python) echo "$PYTHON_OUT" ;;
        typescript) echo "$TS_OUT" ;;
        rust) echo "$RUST_OUT" ;;
        c) echo "$C_OUT" ;;
    esac
}

# Language to output extension
lang_to_outext() {
    case $1 in
        python) echo "py" ;;
        typescript) echo "ts" ;;
        rust) echo "rs" ;;
        c) echo "c" ;;
    esac
}

# Language to source extension
lang_to_srcext() {
    case $1 in
        python) echo "fpy" ;;
        typescript) echo "fts" ;;
        rust) echo "frs" ;;
        c) echo "fc" ;;
    esac
}

# Check for markers in file (supports both @marker and @@marker for compatibility)
check_marker() {
    local file="$1"
    local marker="$2"
    head -10 "$file" 2>/dev/null | grep -qE "@@$marker|@$marker"
}

get_timeout() {
    local file="$1"
    local timeout=$(head -10 "$file" 2>/dev/null | grep -E "@@timeout|@timeout" | sed 's/.*@@\?timeout[[:space:]]*\([0-9]*\).*/\1/')
    echo "${timeout:-30}"
}

# Increment counter (bash 3.2 compatible)
inc_counter() {
    local lang="$1"
    local counter="$2"
    eval "${lang}_${counter}=\$((${lang}_${counter} + 1))"
}

# Get counter value
get_counter() {
    local lang="$1"
    local counter="$2"
    eval "echo \$${lang}_${counter}"
}

# Run a single test (used in both sequential and parallel modes)
# In parallel mode, writes result to file instead of updating counters
run_single_test() {
    local test_file="$1"
    local lang="$2"
    local result_file="${3:-}"  # Optional: for parallel mode
    local test_name=$(basename "$test_file" | sed 's/\.f[a-z]*$//')
    local target=$(lang_to_target "$lang")
    local out_dir=$(lang_to_outdir "$lang")
    local out_ext=$(lang_to_outext "$lang")
    local out_file="$out_dir/${test_name}.${out_ext}"
    local timeout_val=$(get_timeout "$test_file")

    # Check markers
    if check_marker "$test_file" "skip"; then
        if [ -n "$result_file" ]; then
            echo "skip" > "$result_file"
        else
            echo -e "  ${YELLOW}SKIP${NC} [$lang] $test_name"
            inc_counter "$lang" "skip"
        fi
        return 0
    fi

    local is_xfail=false
    if check_marker "$test_file" "xfail"; then
        is_xfail=true
    fi

    # Compile using framec with proper flags
    local compile_output
    compile_output=$("$FRAMEC" compile -l "$target" -o "$out_dir" "$test_file" 2>&1)
    local compile_status=$?

    if [ $compile_status -ne 0 ] || [ ! -f "$out_file" ]; then
        # xfail tests are expected to fail - report them as XFAIL but count as failures
        if [ -n "$result_file" ]; then
            echo "fail" > "$result_file"
            echo "$compile_output" >> "$result_file"
        else
            if $is_xfail; then
                echo -e "  ${YELLOW}XFAIL${NC} [$lang] $test_name (compile - expected failure)"
            else
                echo -e "  ${RED}FAIL${NC} [$lang] $test_name (compile error)"
                if $VERBOSE; then
                    echo "$compile_output" | head -5 | sed 's/^/    /'
                fi
            fi
            inc_counter "$lang" "fail"
        fi
        return 1
    fi

    if $COMPILE_ONLY; then
        if [ -n "$result_file" ]; then
            echo "pass" > "$result_file"
        else
            echo -e "  ${GREEN}COMPILED${NC} [$lang] $test_name"
            inc_counter "$lang" "pass"
        fi
        return 0
    fi

    # Run (note: timeout command may not be available on macOS)
    local run_output=""
    local run_status=0

    case $lang in
        python)
            run_output=$(python3 "$out_file" 2>&1) || run_status=$?
            ;;
        typescript)
            run_output=$(cd "$TEST_ENV_ROOT/output/typescript" && npx ts-node "tests/${test_name}.ts" 2>&1) || run_status=$?
            ;;
        rust)
            run_output=$(cd "$RUST_CRATE" && cargo run --bin "$test_name" 2>&1) || run_status=$?
            ;;
        c)
            # Compile C with gcc
            local c_bin="$C_OUT/${test_name}"
            local cjson_flags=""
            if [ -d "/opt/homebrew/include/cjson" ]; then
                cjson_flags="-I/opt/homebrew/include -L/opt/homebrew/lib -lcjson"
            elif [ -d "/usr/local/include/cjson" ]; then
                cjson_flags="-I/usr/local/include -L/usr/local/lib -lcjson"
            fi
            if gcc -o "$c_bin" "$out_file" $cjson_flags 2>&1; then
                run_output=$("$c_bin" 2>&1) || run_status=$?
            else
                run_status=1
                run_output="C compilation failed"
            fi
            ;;
    esac

    # Check for PASS in output (legacy) or TAP ok format
    if echo "$run_output" | grep -qE "(^ok |PASS)"; then
        if [ -n "$result_file" ]; then
            echo "pass" > "$result_file"
        else
            echo -e "  ${GREEN}PASS${NC} [$lang] $test_name"
            inc_counter "$lang" "pass"
        fi
        return 0
    else
        # xfail tests are expected to fail - report them as XFAIL but count as failures
        if [ -n "$result_file" ]; then
            echo "fail" > "$result_file"
            echo "$run_output" >> "$result_file"
        else
            if $is_xfail; then
                echo -e "  ${YELLOW}XFAIL${NC} [$lang] $test_name (expected failure)"
            else
                echo -e "  ${RED}FAIL${NC} [$lang] $test_name"
                if $VERBOSE; then
                    echo "$run_output" | head -5 | sed 's/^/    /'
                fi
            fi
            inc_counter "$lang" "fail"
        fi
        return 1
    fi
}

# Collect all test files for a language
collect_tests_for_lang() {
    local lang="$1"
    local ext=$(lang_to_srcext "$lang")
    local tests=""

    # Common tests
    if [ -d "$SCRIPT_DIR/common/positive" ]; then
        for category_dir in "$SCRIPT_DIR/common/positive"/*/; do
            [ -d "$category_dir" ] || continue
            if [ -n "$FILTER_CATEGORY" ]; then
                local cat_name=$(basename "$category_dir")
                [ "$cat_name" != "$FILTER_CATEGORY" ] && continue
            fi
            for f in "$category_dir"/*.$ext; do
                [ -f "$f" ] && tests="$tests$f"$'\n'
            done
        done
    fi

    # Language-specific tests
    if [ -d "$SCRIPT_DIR/$lang" ]; then
        for category_dir in "$SCRIPT_DIR/$lang"/*/; do
            [ -d "$category_dir" ] || continue
            if [ -n "$FILTER_CATEGORY" ]; then
                local cat_name=$(basename "$category_dir")
                [ "$cat_name" != "$FILTER_CATEGORY" ] && continue
            fi
            for f in "$category_dir"/*.$ext; do
                [ -f "$f" ] && tests="$tests$f"$'\n'
            done
        done
    fi

    echo "$tests" | sort -u | grep -v '^$'
}

# Run all tests for a language in parallel (within the language)
run_lang_parallel() {
    local lang="$1"
    local lang_results_dir="$RESULTS_DIR/$lang"
    mkdir -p "$lang_results_dir"

    local tests=$(collect_tests_for_lang "$lang")
    [ -z "$tests" ] && return 0

    local test_count=$(echo "$tests" | wc -l | tr -d ' ')
    echo -e "${BLUE}[$lang] Running $test_count tests with $JOBS parallel jobs...${NC}"

    # Export necessary variables for helper script
    export FRAMEC TEST_ENV_ROOT

    # Use helper script with xargs -P for parallel execution
    # Use hash of full path for unique result filename to avoid collisions
    echo "$tests" | while read test_file; do
        [ -z "$test_file" ] && continue
        # Create unique ID from path to avoid name collisions across directories
        # Use cksum for portability (works on both macOS and Linux)
        local unique_id=$(echo "$test_file" | cksum | cut -d' ' -f1)
        local test_name=$(basename "$test_file" | sed 's/\.f[a-z]*$//')
        echo "$test_file $lang $lang_results_dir/${test_name}_${unique_id}.result"
    done | xargs -P "$JOBS" -L 1 "$SCRIPT_DIR/run_single_test.sh"
}

# Aggregate results from parallel run (first pass - collect failures for rerun)
aggregate_results_first_pass() {
    local lang="$1"
    local lang_results_dir="$RESULTS_DIR/$lang"
    local failures_file="$RESULTS_DIR/${lang}_failures.txt"

    [ -d "$lang_results_dir" ] || return

    > "$failures_file"  # Clear failures file

    for result_file in "$lang_results_dir"/*.result; do
        [ -f "$result_file" ] || continue
        # Extract test name (remove _<cksum> suffix)
        local filename=$(basename "$result_file" .result)
        local test_name=$(echo "$filename" | sed 's/_[0-9]*$//')
        local result=$(head -1 "$result_file")
        # Get original test file path from line 2 if stored, otherwise skip rerun
        local test_path=$(sed -n '2p' "$result_file" 2>/dev/null | grep "^TEST_FILE:" | cut -d: -f2-)

        case "$result" in
            pass)
                echo -e "  ${GREEN}PASS${NC} [$lang] $test_name"
                inc_counter "$lang" "pass"
                ;;
            fail)
                # Don't print yet - collect for rerun
                if [ -n "$test_path" ]; then
                    echo "$test_path" >> "$failures_file"
                else
                    # Can't rerun without path, count as fail
                    echo -e "  ${RED}FAIL${NC} [$lang] $test_name"
                    if $VERBOSE; then
                        tail -n +2 "$result_file" | head -5 | sed 's/^/    /'
                    fi
                    inc_counter "$lang" "fail"
                fi
                ;;
            skip)
                echo -e "  ${YELLOW}SKIP${NC} [$lang] $test_name"
                inc_counter "$lang" "skip"
                ;;
            known)
                echo -e "  ${YELLOW}XFAIL${NC} [$lang] $test_name"
                inc_counter "$lang" "known"
                ;;
        esac
    done
}

# Rerun failed tests sequentially to confirm failures
rerun_failures() {
    local lang="$1"
    local failures_file="$RESULTS_DIR/${lang}_failures.txt"

    [ -f "$failures_file" ] || return
    local failure_count=$(wc -l < "$failures_file" | tr -d ' ')
    [ "$failure_count" -eq 0 ] && return

    echo -e "  ${YELLOW}Rerunning $failure_count failed $lang tests...${NC}"

    while read test_file; do
        [ -z "$test_file" ] && continue
        local test_name=$(basename "$test_file" | sed 's/\.f[a-z]*$//')

        # Rerun the test sequentially
        local rerun_result_file="$RESULTS_DIR/${lang}_rerun_${test_name}.result"
        "$SCRIPT_DIR/run_single_test.sh" "$test_file" "$lang" "$rerun_result_file" 2>/dev/null

        local result=$(head -1 "$rerun_result_file" 2>/dev/null)
        case "$result" in
            pass)
                echo -e "  ${GREEN}PASS${NC} [$lang] $test_name (passed on rerun)"
                inc_counter "$lang" "pass"
                ;;
            fail)
                echo -e "  ${RED}FAIL${NC} [$lang] $test_name"
                if $VERBOSE; then
                    tail -n +2 "$rerun_result_file" | head -5 | sed 's/^/    /'
                fi
                inc_counter "$lang" "fail"
                ;;
            *)
                echo -e "  ${RED}FAIL${NC} [$lang] $test_name (rerun failed)"
                inc_counter "$lang" "fail"
                ;;
        esac
    done < "$failures_file"
}

# Discover and run tests in a directory (sequential mode)
run_category() {
    local category_dir="$1"
    local category_name=$(basename "$category_dir")
    # Get scope - handle nested structure (common/positive/<category>)
    local parent_dir=$(dirname "$category_dir")
    local scope=$(basename "$parent_dir")
    # If parent is 'positive', scope is actually 'common'
    if [ "$scope" = "positive" ]; then
        scope="common"
        category_name="positive/$category_name"
    fi

    # Skip if filtering by category and doesn't match
    if [ -n "$FILTER_CATEGORY" ] && [ "$category_name" != "$FILTER_CATEGORY" ]; then
        return
    fi

    # Check if directory has test files
    local has_tests=false
    for ext in fpy fts frs fc; do
        if ls "$category_dir"/*.$ext 1>/dev/null 2>&1; then
            has_tests=true
            break
        fi
    done

    if ! $has_tests; then
        return
    fi

    echo ""
    echo -e "${BLUE}=== $scope/$category_name ===${NC}"

    # Determine which languages to test based on scope
    local languages=""
    case $scope in
        common) languages="python typescript rust c" ;;
        python) languages="python" ;;
        typescript) languages="typescript" ;;
        rust) languages="rust" ;;
        c) languages="c" ;;
    esac

    # Get unique test names from all language files
    local test_names=""
    for ext in fpy fts frs fc; do
        for f in "$category_dir"/*.$ext; do
            [ -f "$f" ] || continue
            local name=$(basename "$f" | sed 's/\.f[a-z]*$//')
            if ! echo "$test_names" | grep -q "^${name}$"; then
                test_names="$test_names$name"$'\n'
            fi
        done
    done

    # Sort test names
    test_names=$(echo "$test_names" | sort -u)

    # Run each test for applicable languages
    for test_name in $test_names; do
        [ -z "$test_name" ] && continue

        for lang in $languages; do
            # Skip if filtering by language and doesn't match
            if [ -n "$FILTER_LANG" ] && [ "$lang" != "$FILTER_LANG" ]; then
                continue
            fi
            # Skip if filtering by multiple languages and doesn't match
            if [ -n "$FILTER_LANGS" ] && ! echo "$FILTER_LANGS" | grep -qw "$lang"; then
                continue
            fi

            # Get extension for this language
            local ext=""
            case $lang in
                python) ext="fpy" ;;
                typescript) ext="fts" ;;
                rust) ext="frs" ;;
                c) ext="fc" ;;
            esac

            local test_file="$category_dir/${test_name}.${ext}"

            # Skip if file doesn't exist for this language
            [ -f "$test_file" ] || continue

            run_single_test "$test_file" "$lang"
        done
    done
}

# Print header
echo "=========================================="
echo "Frame V4 Test Runner"
echo "=========================================="
echo "Transpiler: $FRAMEC"
echo "Test root:  $SCRIPT_DIR"
echo "Output:     $TEST_ENV_ROOT/output/"
[ -n "$FILTER_LANG" ] && echo "Language:   $FILTER_LANG"
[ -n "$FILTER_LANGS" ] && echo "Languages:  $FILTER_LANGS"
[ -n "$FILTER_CATEGORY" ] && echo "Category:   $FILTER_CATEGORY"
$PARALLEL && echo "Mode:       Parallel ($JOBS jobs)" || echo "Mode:       Sequential"

if $PARALLEL; then
    # ========================================
    # PARALLEL MODE
    # ========================================
    echo ""
    echo -e "${BLUE}Running all languages in parallel...${NC}"

    # Determine which languages to run
    if [ -n "$FILTER_LANG" ]; then
        languages="$FILTER_LANG"
    elif [ -n "$FILTER_LANGS" ]; then
        languages="$FILTER_LANGS"
    else
        languages="python typescript rust c"
    fi

    # Phase 1: Transpile all tests first (all languages in parallel)
    echo -e "${BLUE}Phase 1: Transpiling all tests...${NC}"
    for lang in $languages; do
        tests=$(collect_tests_for_lang "$lang")
        [ -z "$tests" ] && continue
        target=$(lang_to_target "$lang")
        out_dir=$(lang_to_outdir "$lang")
        echo "$tests" | xargs -P "$JOBS" -I {} "$FRAMEC" compile -l "$target" -o "$out_dir" {} 2>/dev/null &
    done
    wait

    # Phase 2: Build Rust binaries (single cargo build for all)
    if echo "$languages" | grep -q "rust"; then
        echo -e "${BLUE}[rust] Building all binaries...${NC}"
        (cd "$RUST_CRATE" && cargo build --release --bins --jobs "$JOBS" 2>&1 | grep -E "Compiling|Finished|error" || true)
    fi

    echo -e "${BLUE}Phase 2: Running all tests...${NC}"

    # Run all languages in parallel (each language runs its tests in parallel internally)
    pids=""
    for lang in $languages; do
        (
            run_lang_parallel "$lang"
        ) &
        pids="$pids $!"
    done

    # Wait for all languages to complete
    for pid in $pids; do
        wait $pid 2>/dev/null || true
    done

    echo ""
    echo -e "${BLUE}Aggregating results...${NC}"

    # First pass: aggregate results and collect failures
    for lang in $languages; do
        aggregate_results_first_pass "$lang"
    done

    # Rerun any failures sequentially to confirm they're real failures
    has_failures=false
    for lang in $languages; do
        failures_file="$RESULTS_DIR/${lang}_failures.txt"
        if [ -f "$failures_file" ] && [ -s "$failures_file" ]; then
            has_failures=true
            break
        fi
    done

    if $has_failures; then
        echo ""
        echo -e "${BLUE}Rerunning failures to confirm...${NC}"
        for lang in $languages; do
            rerun_failures "$lang"
        done
    fi

    # Run error tests (these are usually quick and sequential is fine)
    for error_type in compile-error transpile-error runtime-error; do
        error_dir="$SCRIPT_DIR/common/$error_type"
        if [ -d "$error_dir" ] && [ -x "$error_dir/run_tests.sh" ]; then
            echo -e "${BLUE}=== common/$error_type ===${NC}"
            "$error_dir/run_tests.sh" 2>&1 | grep -v "^TAP version" | grep -v "^1\.\." | sed 's/^ok /  PASS - /' | sed 's/^not ok /  FAIL - /'
        fi
    done

else
    # ========================================
    # SEQUENTIAL MODE (original behavior)
    # ========================================

    # Discover and run all categories
    # Handle common/positive/* separately (nested structure)
    if [ -d "$SCRIPT_DIR/common/positive" ]; then
        for category_dir in "$SCRIPT_DIR/common/positive"/*/; do
            [ -d "$category_dir" ] || continue
            run_category "$category_dir"
        done
    fi

    # Run specialized error test runners
    for error_type in compile-error transpile-error runtime-error; do
        error_dir="$SCRIPT_DIR/common/$error_type"
        if [ -d "$error_dir" ] && [ -x "$error_dir/run_tests.sh" ]; then
            echo -e "${BLUE}=== common/$error_type ===${NC}"
            "$error_dir/run_tests.sh" 2>&1 | grep -v "^TAP version" | grep -v "^1\.\." | sed 's/^ok /  PASS - /' | sed 's/^not ok /  FAIL - /'
        fi
    done

    # Language-specific test directories
    for scope_dir in "$SCRIPT_DIR/python" "$SCRIPT_DIR/typescript" "$SCRIPT_DIR/rust" "$SCRIPT_DIR/c"; do
        [ -d "$scope_dir" ] || continue

        for category_dir in "$scope_dir"/*/; do
            [ -d "$category_dir" ] || continue
            run_category "$category_dir"
        done
    done
fi

# Summary
echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="

total_pass=0
total_fail=0
total_skip=0
total_known=0

for lang in python typescript rust c; do
    p=$(get_counter "$lang" "pass")
    f=$(get_counter "$lang" "fail")
    s=$(get_counter "$lang" "skip")
    k=$(get_counter "$lang" "known")
    total=$((p + f + s + k))

    [ $total -eq 0 ] && continue

    total_pass=$((total_pass + p))
    total_fail=$((total_fail + f))
    total_skip=$((total_skip + s))
    total_known=$((total_known + k))

    printf "%-12s ${GREEN}%3d passed${NC}  ${RED}%3d failed${NC}  ${YELLOW}%3d skipped${NC}\n" \
        "$lang:" "$p" "$f" "$s"
done

echo ""
echo "Total: $total_pass passed, $total_fail failed, $total_skip skipped"

# Exit with failure if any tests failed
[ $total_fail -gt 0 ] && exit 1
exit 0
