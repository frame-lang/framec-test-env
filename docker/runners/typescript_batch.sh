#!/bin/bash
# Batched TypeScript test runner. Each .fts transpiled to a standalone .ts
# module. TestRunner.ts dynamically imports each module; one tsx cold start
# covers the whole run vs. one per test today.

set -uo pipefail

# Source-hash cache for framec: skips re-transpile when source
# + framec version haven't changed since last run.
. /framec_cached.sh

OUTPUT="/output"
COMPILE_DIR="/tmp/ts_out"
MANIFEST="/tmp/ts_manifest.tsv"
RUNNER="/opt/TestRunner.ts"
COMPILE_ONLY="${COMPILE_ONLY:-false}"

target="typescript"
ext="fts"
out_ext="ts"

mkdir -p "$OUTPUT"
rm -rf "$COMPILE_DIR" "$MANIFEST" 2>/dev/null
mkdir -p "$COMPILE_DIR"
: > "$MANIFEST"

tests=$(find /tests/common/positive -name "*.$ext" 2>/dev/null | sort)
lang_tests=$(find /tests/typescript -name "*.$ext" 2>/dev/null | sort)
if [ -n "$lang_tests" ]; then
    tests="$tests
$lang_tests"
fi

test_count=$(echo "$tests" | grep -c . || echo 0)
if [ "$test_count" -eq 0 ]; then
    echo "TAP version 14"
    echo "1..0 # SKIP no typescript tests found"
    exit 0
fi

echo "TAP version 14"
echo "1..$test_count"

test_num=0

for test_file in $tests; do
    test_num=$((test_num + 1))
    test_name=$(basename "$test_file" ".$ext")

    if head -10 "$test_file" 2>/dev/null | grep -qE "@@skip|@skip"; then
        printf '%s\tSKIP\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    sanitized=$(printf '%s' "$test_name" | sed 's/[^A-Za-z0-9_]/_/g')
    # Prefix with test_num so duplicate basenames (e.g. two
    # forward_parent tests in different categories) get unique ids.
    sanitized="t${test_num}_${sanitized}"
    # Give each test its own output directory so framec's "name output
    # after the source file" behaviour doesn't collide when two tests
    # share a basename (different category dirs but same leaf name).
    test_out_dir="$COMPILE_DIR/${sanitized}"
    rm -rf "$test_out_dir" 2>/dev/null
    mkdir -p "$test_out_dir"
    ts_path="$test_out_dir/${sanitized}.ts"

    if ! framec_cached "$target" "$test_out_dir" "$test_file" /tmp/compile_err; then
        if echo "$test_file" | grep -q "transpile-error"; then
            printf '%s\tTRANSPILE_ERROR_OK\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        else
            err_line=$(head -5 /tmp/compile_err 2>/dev/null | tr '\n' '\\' | sed 's/\\$//' | sed 's/\\/\\n/g')
            printf '%s\tTRANSPILE_FAIL\t%s\t\t%s\n' "$test_num" "$test_name" "$err_line" >> "$MANIFEST"
        fi
        continue
    fi

    src=$(ls "$test_out_dir"/*.ts 2>/dev/null | head -1)
    if [ -z "$src" ]; then
        printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi
    if [ "$src" != "$ts_path" ]; then
        mv "$src" "$ts_path"
    fi

    if [ "$COMPILE_ONLY" = "true" ]; then
        printf '%s\tCOMPILE_ONLY\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    printf '%s\tRUN\t%s\t%s\n' "$test_num" "$test_name" "$ts_path" >> "$MANIFEST"
done

if [ "$COMPILE_ONLY" = "true" ]; then
    pass=0; fail=0; skip=0
    while IFS=$'\t' read -r num status name rest; do
        case "$status" in
            SKIP)                   echo "ok $num - $name # SKIP";                              skip=$((skip+1)) ;;
            TRANSPILE_ERROR_OK)     echo "ok $num - $name # correctly rejected by transpiler";  pass=$((pass+1)) ;;
            TRANSPILE_FAIL)         echo "not ok $num - $name # transpile failed";              fail=$((fail+1)) ;;
            NO_OUTPUT)              echo "not ok $num - $name # no output file";                fail=$((fail+1)) ;;
            COMPILE_ONLY|RUN)       echo "ok $num - $name # transpiled";                        pass=$((pass+1)) ;;
        esac
    done < "$MANIFEST"
    echo ""
    echo "# typescript: $pass passed, $fail failed, $skip skipped"
    exit $fail
fi

# Integrity check — verify dispatcher emitted test_count TAP lines.
tap_out=$(mktemp)
tsx "$RUNNER" "$MANIFEST" | tee "$tap_out"
rc=${PIPESTATUS[0]:-$?}
emitted=$(grep -cE "^(ok |not ok )" "$tap_out" || true)
rm -f "$tap_out"
if [ "$emitted" -ne "$test_count" ]; then
    echo "not ok $((test_count + 1)) - __harness_integrity__ # expected $test_count TAP lines, got $emitted"
    [ "$rc" = "0" ] && rc=1
fi
exit $rc