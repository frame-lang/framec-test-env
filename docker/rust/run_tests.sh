#!/bin/bash
# Rust test runner - discovers, compiles, runs tests, emits TAP

set -e

# Find all Rust test files
tests=$(find /tests/common /tests/rust -name "*.frs" 2>/dev/null | sort)
test_count=$(echo "$tests" | grep -c . || echo 0)

if [ "$test_count" -eq 0 ]; then
    echo "TAP version 14"
    echo "1..0 # SKIP no Rust tests found"
    exit 0
fi

echo "TAP version 14"
echo "1..$test_count"

test_num=0
for test_file in $tests; do
    test_num=$((test_num + 1))
    test_name=$(basename "$test_file" .frs)

    # Compile Frame to Rust
    if ! framec compile -l rust -o /tmp/out "$test_file" 2>/tmp/compile_err; then
        echo "not ok $test_num - $test_name # compile failed"
        echo "  ---"
        cat /tmp/compile_err | sed 's/^/  # /'
        echo "  ..."
        continue
    fi

    out_file="/tmp/out/${test_name}.rs"
    if [ ! -f "$out_file" ]; then
        echo "not ok $test_num - $test_name # no output file"
        continue
    fi

    # Copy to cargo project and build
    cp "$out_file" /rust_runner/src/main.rs

    if ! (cd /rust_runner && cargo build --release 2>/tmp/build_err); then
        echo "not ok $test_num - $test_name # cargo build failed"
        echo "  ---"
        cat /tmp/build_err | tail -20 | sed 's/^/  # /'
        echo "  ..."
        continue
    fi

    # Run
    if output=$(/rust_runner/target/release/runner 2>&1); then
        # Check for PASS in output (legacy) or TAP ok
        if echo "$output" | grep -qE "(^ok |PASS)"; then
            echo "ok $test_num - $test_name"
        else
            echo "not ok $test_num - $test_name # no PASS in output"
            echo "  ---"
            echo "$output" | head -10 | sed 's/^/  # /'
            echo "  ..."
        fi
    else
        echo "not ok $test_num - $test_name # runtime error"
        echo "  ---"
        echo "$output" | head -10 | sed 's/^/  # /'
        echo "  ..."
    fi
done
