#!/bin/bash
#
# Helper script to run a single Frame test
# Called by run_tests.sh in parallel mode
#
# Usage: ./run_single_test.sh <test_file> <lang> <result_file>
#

test_file="$1"
lang="$2"
result_file="$3"

# Ensure all tool directories are in PATH (non-login shells like CI / Claude Code
# don't source the user's profile). Matches run_tests.sh — both need this so
# python3, node, npx, cargo, gcc are always reachable.
for __dir in "$HOME/.cargo/bin" "/usr/local/bin" "/opt/homebrew/bin"; do
    if [ -d "$__dir" ]; then
        case ":$PATH:" in
            *":$__dir:"*) ;;
            *) export PATH="$__dir:$PATH" ;;
        esac
    fi
done
unset __dir

# Environment (inherited from parent)
FRAMEC="${FRAMEC:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"
TEST_ENV_ROOT="${TEST_ENV_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"

PYTHON_OUT="$TEST_ENV_ROOT/output/python/tests"
TS_OUT="$TEST_ENV_ROOT/output/typescript/tests"
RUST_CRATE="$TEST_ENV_ROOT/output/rust"
RUST_OUT="$RUST_CRATE/tests"
C_OUT="$TEST_ENV_ROOT/output/c/tests"
CPP_OUT="$TEST_ENV_ROOT/output/cpp/tests"
JAVA_OUT="$TEST_ENV_ROOT/output/java/tests"
CSHARP_OUT="$TEST_ENV_ROOT/output/csharp/tests"

# .NET SDK — find dotnet
DOTNET_CMD=""
for __ddir in "/usr/local/opt/dotnet/libexec" "/opt/homebrew/opt/dotnet/libexec" "/usr/share/dotnet"; do
    if [ -x "$__ddir/dotnet" ]; then
        DOTNET_CMD="$__ddir/dotnet"
        export DOTNET_ROOT="$__ddir"
        break
    fi
done

# Java 17 — find JDK
JAVA_HOME_17=""
for __jdir in "/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home" "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home" "/usr/lib/jvm/java-17-openjdk-amd64"; do
    if [ -x "$__jdir/bin/javac" ]; then
        JAVA_HOME_17="$__jdir"
        break
    fi
done

test_name=$(basename "$test_file" | sed 's/\.f[a-z]*$//')

# Language mappings
case $lang in
    python) target="python_3"; out_dir="$PYTHON_OUT"; out_ext="py" ;;
    typescript) target="typescript"; out_dir="$TS_OUT"; out_ext="ts" ;;
    rust) target="rust"; out_dir="$RUST_OUT"; out_ext="rs" ;;
    c) target="c"; out_dir="$C_OUT"; out_ext="c" ;;
    cpp) target="cpp_17"; out_dir="$CPP_OUT"; out_ext="cpp" ;;
    java) target="java"; out_dir="$JAVA_OUT"; out_ext="java" ;;
    csharp) target="csharp"; out_dir="$CSHARP_OUT"; out_ext="cs" ;;
esac

out_file="$out_dir/${test_name}.${out_ext}"

# Check skip marker
if head -10 "$test_file" 2>/dev/null | grep -qE "@@skip|@skip"; then
    echo "skip" > "$result_file"
    exit 0
fi

# Check xfail marker
is_xfail=false
if head -10 "$test_file" 2>/dev/null | grep -qE "@@xfail|@xfail"; then
    is_xfail=true
fi

# Transpile
compile_output=$("$FRAMEC" compile -l "$target" -o "$out_dir" "$test_file" 2>&1)
compile_status=$?

if [ $compile_status -ne 0 ] || [ ! -f "$out_file" ]; then
    if $is_xfail; then
        echo "known" > "$result_file"
    else
        echo "fail" > "$result_file"
        echo "TEST_FILE:$test_file" >> "$result_file"
        echo "$compile_output" >> "$result_file"
    fi
    exit 0
fi

# Run
run_output=""
run_status=0

case $lang in
    python)
        run_output=$(python3 "$out_file" 2>&1) || run_status=$?
        ;;
    typescript)
        run_output=$(cd "$TEST_ENV_ROOT/output/typescript" && npx ts-node "tests/${test_name}.ts" 2>&1) || run_status=$?
        ;;
    rust)
        # Run pre-built binary directly (cargo build was done before parallel execution)
        rust_bin="$RUST_CRATE/target/release/$test_name"
        if [ -x "$rust_bin" ]; then
            run_output=$("$rust_bin" 2>&1) || run_status=$?
        else
            # Fallback to debug build
            rust_bin="$RUST_CRATE/target/debug/$test_name"
            if [ -x "$rust_bin" ]; then
                run_output=$("$rust_bin" 2>&1) || run_status=$?
            else
                run_status=1
                run_output="Rust binary not found: $test_name"
            fi
        fi
        ;;
    c)
        c_bin="$C_OUT/${test_name}"
        cjson_flags=""
        # Prefer /opt/homebrew (ARM64 Mac) over /usr/local (may be x86_64)
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
    cpp)
        cpp_bin="$CPP_OUT/${test_name}"
        cpp_json_flags=""
        if [ -d "/opt/homebrew/include/nlohmann" ]; then
            cpp_json_flags="-I/opt/homebrew/include"
        elif [ -d "/usr/local/include/nlohmann" ]; then
            cpp_json_flags="-I/usr/local/include"
        fi
        if g++ -std=c++17 $cpp_json_flags -o "$cpp_bin" "$out_file" 2>&1; then
            run_output=$("$cpp_bin" 2>&1) || run_status=$?
        else
            run_status=1
            run_output="C++ compilation failed"
        fi
        ;;
    java)
        if [ -n "$JAVA_HOME_17" ]; then
            javac_cmd="$JAVA_HOME_17/bin/javac"
            java_cmd="$JAVA_HOME_17/bin/java"
        else
            javac_cmd="javac"
            java_cmd="java"
        fi
        java_json_jar="$TEST_ENV_ROOT/output/java/lib/json.jar"
        java_cp="$JAVA_OUT"
        if [ -f "$java_json_jar" ]; then
            java_cp="$JAVA_OUT:$java_json_jar"
        fi
        if $javac_cmd -cp "$java_cp" -d "$JAVA_OUT" "$out_file" 2>&1; then
            run_output=$($java_cmd -cp "$java_cp" Main 2>&1) || run_status=$?
        else
            run_status=1
            run_output="Java compilation failed"
        fi
        ;;
    csharp)
        if [ -n "$DOTNET_CMD" ]; then
            run_output=$(DOTNET_ROOT="$DOTNET_ROOT" $DOTNET_CMD run "$out_file" 2>&1) || run_status=$?
        else
            run_status=1
            run_output="dotnet not found"
        fi
        ;;
esac

# Determine pass/fail:
#   1. Non-zero exit code = definite failure
#   2. TAP "not ok" lines = failure (even if exit code is 0)
#   3. TAP "ok" lines or "PASS" string = pass
#   4. No recognizable output = failure
test_passed=false
if [ $run_status -ne 0 ]; then
    test_passed=false
elif echo "$run_output" | grep -q "^not ok "; then
    test_passed=false
elif echo "$run_output" | grep -qE "(^ok |PASS)"; then
    test_passed=true
fi

if $test_passed; then
    echo "pass" > "$result_file"
elif $is_xfail; then
    echo "known" > "$result_file"
else
    echo "fail" > "$result_file"
    echo "TEST_FILE:$test_file" >> "$result_file"
    echo "$run_output" >> "$result_file"
fi
