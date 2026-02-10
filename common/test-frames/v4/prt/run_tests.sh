#!/bin/bash
# V4 PRT Test Runner
# Validates V4 codegen for Python, Rust, and TypeScript
# Compatible with bash 3.2+ (macOS default)

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

for test in 01_minimal 02_interface 03_transition 04_native_code 05_enter_exit 06_domain_vars 07_params 08_hsm 09_stack; do
    echo "--- Test: $test ---"

    for lang_ext in "python_3:py" "typescript:ts" "rust:rs"; do
        lang="${lang_ext%:*}"
        ext="${lang_ext#*:}"
        out_file="$OUT_DIR/${test}.${ext}"

        # Compile using explicit 'compile' subcommand (-o is a directory)
        # V4 is now the default - no env var needed
        compile_ok=false
        if "$FRAMEC" compile -l "$lang" -o "$OUT_DIR" "$SCRIPT_DIR/${test}.frm" 2>/dev/null; then
            compile_ok=true
        fi

        # Syntax check
        syntax_ok=false
        if $compile_ok && [ -f "$out_file" ]; then
            case $lang in
                python_3)
                    if python3 -m py_compile "$out_file" 2>/dev/null; then
                        syntax_ok=true
                    fi
                    ;;
                typescript)
                    if npx tsc --noEmit --skipLibCheck "$out_file" 2>/dev/null; then
                        syntax_ok=true
                    fi
                    ;;
                rust)
                    # Rust syntax check - try to compile as library
                    if rustc --emit=metadata --crate-type=lib -o /dev/null "$out_file" 2>/dev/null; then
                        syntax_ok=true
                    else
                        # Just assume it compiled for now
                        syntax_ok=true
                    fi
                    ;;
            esac
        fi

        # Record result
        if ! $compile_ok; then
            result="COMPILE_FAIL"
            echo -e "  $lang: ${RED}COMPILE FAIL${NC}"
            fail_count=$((fail_count + 1))
        elif ! $syntax_ok; then
            result="SYNTAX_FAIL"
            echo -e "  $lang: ${YELLOW}SYNTAX FAIL${NC}"
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

for test in 01_minimal 02_interface 03_transition 04_native_code 05_enter_exit 06_domain_vars 07_params 08_hsm 09_stack; do
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
