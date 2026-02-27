#!/bin/bash
# V4 PRT Test Runner
# Validates V4 codegen for Python, Rust, TypeScript, and C
# Compatible with bash 3.2+ (macOS default)
#
# Test file resolution:
#   - If a language-specific test exists in prt/<lang>/<test>.frm, use it
#   - Otherwise, fall back to the shared test in prt/<test>.frm
#   - This allows tests with language-specific native code
#
# Output directories:
#   - Python: framepiler_test_env/python_test_crate/tests/
#   - TypeScript: framepiler_test_env/typescript_test_crate/tests/
#   - Rust: framepiler_test_env/rust_test_crate/tests/

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FRAMEC="${FRAMEC:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"

# Test environment root (framepiler_test_env/)
# From tests/common/primary/ go up: primary -> common -> tests -> framepiler_test_env
TEST_ENV_ROOT="${FRAMEPILER_TEST_ENV:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"

# Language-specific output directories
PYTHON_OUT="${PYTHON_OUT:-$TEST_ENV_ROOT/output/python/tests}"
TS_OUT="${TS_OUT:-$TEST_ENV_ROOT/output/typescript/tests}"
RUST_CRATE="${RUST_CRATE:-$TEST_ENV_ROOT/output/rust}"
RUST_OUT="$RUST_CRATE/tests"
C_OUT="${C_OUT:-$TEST_ENV_ROOT/output/c/tests}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Create output directories
mkdir -p "$PYTHON_OUT"
mkdir -p "$TS_OUT"
mkdir -p "$RUST_OUT"
mkdir -p "$C_OUT"

echo "=========================================="
echo "V4 PRT Test Suite"
echo "=========================================="
echo "Using framec: $FRAMEC"
echo "Test env root: $TEST_ENV_ROOT"
echo "Python output: $PYTHON_OUT"
echo "TypeScript output: $TS_OUT"
echo "Rust output: $RUST_OUT"
echo "C output: $C_OUT"
echo ""

pass_count=0
fail_count=0
results=""

# Map language to file extension
lang_to_ext() {
    case $1 in
        python_3) echo "fpy" ;;
        typescript) echo "fts" ;;
        rust) echo "frs" ;;
        c) echo "fc" ;;
        *) echo "frm" ;;
    esac
}

# Get output directory for language
lang_to_outdir() {
    case $1 in
        python_3) echo "$PYTHON_OUT" ;;
        typescript) echo "$TS_OUT" ;;
        rust) echo "$RUST_OUT" ;;
        c) echo "$C_OUT" ;;
    esac
}

# Get output file extension
lang_to_outext() {
    case $1 in
        python_3) echo "py" ;;
        typescript) echo "ts" ;;
        rust) echo "rs" ;;
        c) echo "c" ;;
    esac
}

for test in 01_interface_return 02_interface 03_transition 04_native_code 05_enter_exit 06_domain_vars 07_params 08_hsm 09_stack 10_state_var_basic 11_state_var_reentry 12_state_var_push_pop 13_system_return 14_system_return_default 15_system_return_chain 16_system_return_reentrant 17_transition_enter_args 18_transition_exit_args 19_transition_forward 20_transition_pop 21_actions_basic 22_operations_basic 23_persist_basic 24_persist_roundtrip 25_persist_stack 26_state_params 29_forward_enter_first 30_hsm_default_forward 31_doc_lamp_basic 32_doc_lamp_hsm 33_doc_history_basic 34_doc_history_hsm 35_return_init 36_context_basic 37_context_reentrant 38_context_data; do
    echo "--- Test: $test ---"

    for lang in python_3 typescript rust c; do
        frame_ext=$(lang_to_ext "$lang")
        out_dir=$(lang_to_outdir "$lang")
        out_ext=$(lang_to_outext "$lang")
        out_file="$out_dir/${test}.${out_ext}"

        # Determine which test file to use
        test_file="$SCRIPT_DIR/${test}.${frame_ext}"

        # Compile using explicit 'compile' subcommand
        compile_ok=false
        if "$FRAMEC" compile -l "$lang" -o "$out_dir" "$test_file" 2>/dev/null; then
            compile_ok=true
        fi

        # Run the test
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
                    # Run from the typescript output directory (has node_modules)
                    run_output=$(cd "$TEST_ENV_ROOT/output/typescript" && npx ts-node "tests/${test}.ts" 2>&1)
                    if echo "$run_output" | grep -q "PASS"; then
                        run_ok=true
                    fi
                    ;;
                rust)
                    # All Rust tests run via cargo (has dependencies)
                    run_output=$(cd "$RUST_CRATE" && cargo run --bin "$test" 2>&1)
                    if echo "$run_output" | grep -q "PASS"; then
                        run_ok=true
                    fi
                    ;;
                c)
                    # Compile C with gcc and run
                    c_bin="$C_OUT/${test}"
                    if gcc -o "$c_bin" "$out_file" 2>&1; then
                        run_output=$("$c_bin" 2>&1)
                        if echo "$run_output" | grep -q "PASS"; then
                            run_ok=true
                        fi
                    else
                        run_output="gcc compilation failed"
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

for test in 01_interface_return 02_interface 03_transition 04_native_code 05_enter_exit 06_domain_vars 07_params 08_hsm 09_stack 10_state_var_basic 11_state_var_reentry 12_state_var_push_pop 13_system_return 14_system_return_default 15_system_return_chain 16_system_return_reentrant 17_transition_enter_args 18_transition_exit_args 19_transition_forward 20_transition_pop 21_actions_basic 22_operations_basic 23_persist_basic 24_persist_roundtrip 25_persist_stack 26_state_params 29_forward_enter_first 30_hsm_default_forward 31_doc_lamp_basic 32_doc_lamp_hsm 33_doc_history_basic 34_doc_history_hsm 35_return_init 36_context_basic 37_context_reentrant 38_context_data; do
    line="$test:"
    for lang in python_3 typescript rust c; do
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
echo ""
echo "Generated files:"
echo "  Python: $PYTHON_OUT/*.py"
echo "  TypeScript: $TS_OUT/*.ts"
echo "  Rust: $RUST_OUT/*.rs"
echo "  C: $C_OUT/*.c"

if [ $fail_count -gt 0 ]; then
    exit 1
fi
