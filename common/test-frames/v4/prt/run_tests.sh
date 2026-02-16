#!/bin/bash
# V4 PRT Test Runner
# Validates V4 codegen for Python, Rust, and TypeScript
# Compatible with bash 3.2+ (macOS default)
#
# Test file resolution:
#   - If a language-specific test exists in prt/<lang>/<test>.frm, use it
#   - Otherwise, fall back to the shared test in prt/<test>.frm
#   - This allows tests with language-specific native code

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEC="${FRAMEC:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"
OUT_DIR="${OUT_DIR:-/tmp/v4_prt_tests}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

mkdir -p "$OUT_DIR"

echo "=========================================="
echo "V4 PRT Test Suite"
echo "=========================================="
echo "Using framec: $FRAMEC"
echo "Output dir: $OUT_DIR"
echo ""

pass_count=0
fail_count=0
results=""

# Map language to subdirectory name
lang_to_dir() {
    case $1 in
        python_3) echo "python" ;;
        typescript) echo "typescript" ;;
        rust) echo "rust" ;;
        *) echo "$1" ;;
    esac
}

for test in 01_minimal 02_interface 03_transition 04_native_code 05_enter_exit 06_domain_vars 07_params 08_hsm 09_stack 10_state_var_basic 11_state_var_reentry 12_state_var_push_pop 13_system_return 14_transition_enter_args 15_transition_exit_args; do
    echo "--- Test: $test ---"

    for lang_ext in "python_3:py" "typescript:ts" "rust:rs"; do
        lang="${lang_ext%:*}"
        ext="${lang_ext#*:}"
        out_file="$OUT_DIR/${test}.${ext}"
        lang_dir=$(lang_to_dir "$lang")

        # Determine which test file to use
        # Priority: language-specific > shared
        if [ -f "$SCRIPT_DIR/${lang_dir}/${test}.frm" ]; then
            test_file="$SCRIPT_DIR/${lang_dir}/${test}.frm"
        else
            test_file="$SCRIPT_DIR/${test}.frm"
        fi

        # Compile using explicit 'compile' subcommand (-o is a directory)
        # V4 is now the default - no env var needed
        compile_ok=false
        if "$FRAMEC" compile -l "$lang" -o "$OUT_DIR" "$test_file" 2>/dev/null; then
            compile_ok=true
        fi

        # Run the test (not just syntax check)
        run_ok=false
        run_output=""
        if $compile_ok && [ -f "$out_file" ]; then
            case $lang in
                python_3)
                    run_output=$(python3 "$out_file" 2>&1)
                    if echo "$run_output" | grep -q "PASS"; then
                        run_ok=true
                    fi
                    ;;
                typescript)
                    run_output=$(npx ts-node "$out_file" 2>&1)
                    if echo "$run_output" | grep -q "PASS"; then
                        run_ok=true
                    fi
                    ;;
                rust)
                    exe_file="$OUT_DIR/${test}"
                    if rustc "$out_file" -o "$exe_file" 2>/dev/null; then
                        run_output=$("$exe_file" 2>&1)
                        if echo "$run_output" | grep -q "PASS"; then
                            run_ok=true
                        fi
                    fi
                    ;;
            esac
        fi

        # Record result
        if ! $compile_ok; then
            result="COMPILE_FAIL"
            echo -e "  $lang: ${RED}COMPILE FAIL${NC}"
            fail_count=$((fail_count + 1))
        elif ! $run_ok; then
            result="RUN_FAIL"
            echo -e "  $lang: ${RED}RUN FAIL${NC}"
            if [ -n "$run_output" ]; then
                echo "    Output: $run_output" | head -5
            fi
            fail_count=$((fail_count + 1))
        else
            result="PASS"
            echo -e "  $lang: ${GREEN}PASS${NC}"
            pass_count=$((pass_count + 1))
        fi
        results="$results ${test}_${lang}:${result}"
    done
    echo ""
done

# Summary
echo "=========================================="
echo "Summary"
echo "=========================================="

for test in 01_minimal 02_interface 03_transition 04_native_code 05_enter_exit 06_domain_vars 07_params 08_hsm 09_stack 10_state_var_basic 11_state_var_reentry 12_state_var_push_pop 13_system_return 14_transition_enter_args 15_transition_exit_args; do
    line="$test:"
    for lang in python_3 typescript rust; do
        key="${test}_${lang}"
        # Find result in results string
        result=$(echo "$results" | tr ' ' '\n' | grep "^${key}:" | cut -d: -f2)
        case $result in
            PASS)
                line="$line ${GREEN}[${lang}:OK]${NC}"
                ;;
            *)
                line="$line ${RED}[${lang}:FAIL]${NC}"
                ;;
        esac
    done
    echo -e "$line"
done

echo ""
echo "Total: $pass_count passed, $fail_count failed"

if [ $fail_count -gt 0 ]; then
    exit 1
fi
