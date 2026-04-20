#!/bin/bash
# Batched PHP test runner. One PHP process includes each test file in a
# fresh function scope; stdout captured via ob_start.

set -uo pipefail

# Source-hash cache for framec: skips re-transpile when source
# + framec version haven't changed since last run.
. /framec_cached.sh

OUTPUT="/output"
COMPILE_DIR="/tmp/php_out"
MANIFEST="/tmp/php_manifest.tsv"
RUNNER="/opt/TestRunner.php"
COMPILE_ONLY="${COMPILE_ONLY:-false}"

target="php"
ext="fphp"
out_ext="php"

mkdir -p "$OUTPUT"
rm -rf "$COMPILE_DIR" "$MANIFEST" 2>/dev/null
mkdir -p "$COMPILE_DIR"
: > "$MANIFEST"

tests=$(find /tests/common/positive -name "*.$ext" 2>/dev/null | sort)
lang_tests=$(find /tests/php -name "*.$ext" 2>/dev/null | sort)
if [ -n "$lang_tests" ]; then
    tests="$tests
$lang_tests"
fi

test_count=$(echo "$tests" | grep -c . || echo 0)
if [ "$test_count" -eq 0 ]; then
    echo "TAP version 14"
    echo "1..0 # SKIP no php tests found"
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
    test_src_dir="$COMPILE_DIR/${sanitized}"
    mkdir -p "$test_src_dir"

    if ! framec_cached "$target" "$test_src_dir" "$test_file" /tmp/compile_err; then
        if echo "$test_file" | grep -q "transpile-error"; then
            printf '%s\tTRANSPILE_ERROR_OK\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        else
            err_line=$(head -5 /tmp/compile_err 2>/dev/null | tr '\n' '\\' | sed 's/\\$//' | sed 's/\\/\\n/g')
            printf '%s\tTRANSPILE_FAIL\t%s\t\t%s\n' "$test_num" "$test_name" "$err_line" >> "$MANIFEST"
        fi
        continue
    fi

    src=$(ls "$test_src_dir"/*.php 2>/dev/null | head -1)
    if [ -z "$src" ]; then
        printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    if [ "$COMPILE_ONLY" = "true" ]; then
        printf '%s\tCOMPILE_ONLY\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    # Each test emits `function native() { ... }` (and other helpers) at
    # top level. require-ing multiple tests in one process collides on
    # those symbols — wrap each file in a unique namespace.
    # Strip all `<?php` opening tags from the original (framec may emit
    # them preceded by a blank line or more than once), then emit our own
    # opener plus the namespace header.
    tmp_php=$(mktemp)
    printf '<?php\nnamespace frametest\\%s;\n' "$sanitized" > "$tmp_php"
    sed '/^<?php/d' "$src" >> "$tmp_php"
    mv "$tmp_php" "$src"

    printf '%s\tRUN\t%s\t%s\n' "$test_num" "$test_name" "$src" >> "$MANIFEST"
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
    echo "# php: $pass passed, $fail failed, $skip skipped"
    exit $fail
fi

# Integrity check — verify dispatcher emitted test_count TAP lines.
tap_out=$(mktemp)
php "$RUNNER" "$MANIFEST" | tee "$tap_out"
rc=${PIPESTATUS[0]:-$?}
emitted=$(grep -cE "^(ok |not ok )" "$tap_out" || true)
rm -f "$tap_out"
if [ "$emitted" -ne "$test_count" ]; then
    echo "not ok $((test_count + 1)) - __harness_integrity__ # expected $test_count TAP lines, got $emitted"
    [ "$rc" = "0" ] && rc=1
fi
exit $rc