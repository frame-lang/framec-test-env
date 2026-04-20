#!/bin/bash
# Batched C# test runner. Pattern:
#   1. Transpile every .fcs to .cs, wrapping each test's file contents in
#      `namespace frametest.<sanitized> { ... }` so the `class Program`
#      (and any other helpers Frame emits) live in a unique namespace.
#   2. Copy all .cs files into a pre-built project at /opt/testrunner/tests/
#      alongside TestRunner.cs. One `dotnet build` compiles everything.
#   3. Launch the resulting DLL once, dispatching each test's
#      `frametest.<sanitized>.Program.Main()` by reflection.

set -uo pipefail

# Source-hash cache for framec: skips re-transpile when source
# + framec version haven't changed since last run.
. /framec_cached.sh

OUTPUT="/output"
PROJECT="/opt/testrunner"
TESTS_SRC_DIR="${PROJECT}/tests"
MANIFEST="/tmp/csharp_manifest.tsv"
COMPILE_ONLY="${COMPILE_ONLY:-false}"

target="csharp"
ext="fcs"
out_ext="cs"

mkdir -p "$OUTPUT"
# Clear previous transpiled tests; keep project files and bin/obj for
# incremental build speed.
rm -rf "$TESTS_SRC_DIR" "$MANIFEST" 2>/dev/null
mkdir -p "$TESTS_SRC_DIR"
: > "$MANIFEST"

tests=$(find /tests/common/positive -name "*.$ext" 2>/dev/null | sort)
lang_tests=$(find /tests/csharp -name "*.$ext" 2>/dev/null | sort)
if [ -n "$lang_tests" ]; then
    tests="$tests
$lang_tests"
fi

test_count=$(echo "$tests" | grep -c . || echo 0)
if [ "$test_count" -eq 0 ]; then
    echo "TAP version 14"
    echo "1..0 # SKIP no csharp tests found"
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
    ns="frametest.${sanitized}"
    test_src_dir="$TESTS_SRC_DIR/${sanitized}"
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

    src_cs=$(ls "$test_src_dir"/*.cs 2>/dev/null | head -1)
    if [ -z "$src_cs" ]; then
        printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    if [ "$COMPILE_ONLY" = "true" ]; then
        printf '%s\tCOMPILE_ONLY\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    # Frame emits `using System;` / `using System.Collections.Generic;` at
    # the top of the file, then class declarations. Wrap the whole file in
    # a block-form namespace. `using` inside a namespace is legal in C#.
    tmp_cs=$(mktemp)
    printf 'namespace %s {\n' "$ns" > "$tmp_cs"
    cat "$src_cs" >> "$tmp_cs"
    printf '\n}\n' >> "$tmp_cs"
    mv "$tmp_cs" "$src_cs"

    main_class="${ns}.Program"
    printf '%s\tRUN\t%s\t%s\n' "$test_num" "$test_name" "$main_class" >> "$MANIFEST"
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
    echo "# csharp: $pass passed, $fail failed, $skip skipped"
    exit $fail
fi

# Batch build. One test with a transpiler bug (bool/int conversion,
# null-ref, etc.) poisons the whole batch because the csc compiler
# gives up on the assembly when any file has errors. Recovery strategy:
# on failure, scrape error lines for the offending test subdirectories,
# remove them from the build, mark those tests as COMPILE_FAIL, retry.
# One retry only — if a second failure occurs, mark all remaining RUN
# tests as COMPILE_FAIL and bail.
try_build() {
    dotnet build "$PROJECT" -c Release --nologo >/tmp/dotnet_build.log 2>&1
}

if ! try_build; then
    # Error lines look like:
    #   /opt/testrunner/tests/<sanitized>/<file>.cs(L,C): error CS...
    # Filter to error lines only (not warnings) before extracting dirs.
    bad=$(grep ": error " /tmp/dotnet_build.log \
            | grep -oE "${TESTS_SRC_DIR}/[A-Za-z0-9_]+" \
            | sed "s|${TESTS_SRC_DIR}/||" | sort -u)
    if [ -n "$bad" ]; then
        for s in $bad; do
            tmp_manifest="${MANIFEST}.tmp"
            awk -v s="$s" -F'\t' 'BEGIN{OFS="\t"} {
                if ($2 == "RUN" && index($4, "frametest." s ".") == 1) {
                    $2 = "COMPILE_FAIL"; $4 = ""
                }
                print
            }' "$MANIFEST" > "$tmp_manifest"
            mv "$tmp_manifest" "$MANIFEST"
            rm -rf "${TESTS_SRC_DIR}/${s}"
        done
        if ! try_build; then
            tmp_manifest="${MANIFEST}.tmp"
            awk -F'\t' 'BEGIN{OFS="\t"} {
                if ($2 == "RUN") { $2 = "COMPILE_FAIL"; $4 = "" }
                print
            }' "$MANIFEST" > "$tmp_manifest"
            mv "$tmp_manifest" "$MANIFEST"
            echo "# dotnet build failed even after removing bad files — see below" >&2
            tail -40 /tmp/dotnet_build.log >&2
        fi
    else
        # Failure with no attributable source file — treat as total failure.
        tmp_manifest="${MANIFEST}.tmp"
        awk -F'\t' 'BEGIN{OFS="\t"} {
            if ($2 == "RUN") { $2 = "COMPILE_FAIL"; $4 = "" }
            print
        }' "$MANIFEST" > "$tmp_manifest"
        mv "$tmp_manifest" "$MANIFEST"
        echo "# batch dotnet build failed — see below" >&2
        tail -40 /tmp/dotnet_build.log >&2
    fi
fi

# Integrity check — verify dispatcher emitted test_count TAP lines.
tap_out=$(mktemp)
dotnet "$PROJECT/bin/Release/net8.0/TestRunner.dll" "$MANIFEST" | tee "$tap_out"
rc=${PIPESTATUS[0]:-$?}
emitted=$(grep -cE "^(ok |not ok )" "$tap_out" || true)
rm -f "$tap_out"
if [ "$emitted" -ne "$test_count" ]; then
    echo "not ok $((test_count + 1)) - __harness_integrity__ # expected $test_count TAP lines, got $emitted"
    [ "$rc" = "0" ] && rc=1
fi
exit $rc