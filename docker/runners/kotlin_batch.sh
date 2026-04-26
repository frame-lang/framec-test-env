#!/bin/bash
# Batched Kotlin test runner.
#
# Replaces the per-test kotlinc+java loop in runner.sh with a two-phase flow:
#   1. Transpile every .fkt to .kt (framec, cheap) and write a TSV manifest.
#   2. Batch-compile all .kt files into a single JAR (one kotlinc invocation),
#      then launch /opt/test_runner.jar once to reflectively dispatch each
#      test's main() inside a single JVM.
#
# Net effect: ~2 JVM cold starts per full run instead of ~2N.
#
# Called by runner.sh when LANG=kotlin. The TAP header ("TAP version 14" +
# "1..N") is emitted here; per-test TAP lines are emitted by TestRunner; the
# final "# kotlin: X passed ..." summary is emitted by TestRunner.

set -uo pipefail

# Source-hash cache for framec: skips re-transpile when source
# + framec version haven't changed since last run.
. /framec_cached.sh

OUTPUT="/output"
COMPILE_DIR="/tmp/kotlin_out"
MANIFEST="/tmp/kotlin_manifest.tsv"
ALL_JAR="/tmp/all_tests.jar"
COMPILE_ONLY="${COMPILE_ONLY:-false}"

target="kotlin"
ext="fkt"
out_ext="kt"

mkdir -p "$OUTPUT" "$COMPILE_DIR"
rm -f "$COMPILE_DIR"/*.kt "$MANIFEST" "$ALL_JAR" 2>/dev/null
: > "$MANIFEST"

# Discover test files (same ordering as runner.sh)
tests=$(find /tests/common/positive -name "*.$ext" 2>/dev/null | sort)
lang_tests=$(find /tests/kotlin -name "*.$ext" 2>/dev/null | sort)
if [ -n "$lang_tests" ]; then
    tests="$tests
$lang_tests"
fi

test_count=$(echo "$tests" | grep -c . || echo 0)
if [ "$test_count" -eq 0 ]; then
    echo "TAP version 14"
    echo "1..0 # SKIP no kotlin tests found"
    exit 0
fi

echo "TAP version 14"
echo "1..$test_count"

# ------------------------------------------------------------------
# Phase 1: transpile + build manifest
# ------------------------------------------------------------------
# Manifest rows are TSV: test_num<TAB>STATUS<TAB>test_name[<TAB>main_class[<TAB>extra]]

test_num=0
# Track successfully-transpiled .kt paths for batch compile.
kt_files=""

for test_file in $tests; do
    test_num=$((test_num + 1))
    test_name=$(basename "$test_file" ".$ext")

    # Skip marker
    if head -10 "$test_file" 2>/dev/null | grep -qE "@@skip|@skip"; then
        printf '%s\tSKIP\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    # Compute sanitized (unique per test_num) up-front so we can give each
    # test its own output subdir — otherwise two tests sharing a basename
    # (e.g. forward_parent in different categories) would overwrite each
    # other's on-disk .kt file before compile.
    sanitized=$(printf '%s' "$test_name" | sed 's/[^A-Za-z0-9_]/_/g')
    # Prefix with test_num so duplicate basenames (e.g. two
    # forward_parent tests in different categories) get unique ids.
    sanitized="t${test_num}_${sanitized}"
    test_out_dir="$COMPILE_DIR/${sanitized}"
    rm -rf "$test_out_dir" 2>/dev/null
    mkdir -p "$test_out_dir"

    # Transpile
    if ! framec_cached "$target" "$test_out_dir" "$test_file" /tmp/compile_err; then
        if echo "$test_file" | grep -q "transpile-error"; then
            printf '%s\tTRANSPILE_ERROR_OK\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        else
            err_line=$(head -5 /tmp/compile_err 2>/dev/null | tr '\n' '\\' | sed 's/\\$//' | sed 's/\\/\\n/g')
            printf '%s\tTRANSPILE_FAIL\t%s\t\t%s\n' "$test_num" "$test_name" "$err_line" >> "$MANIFEST"
        fi
        continue
    fi

    per_test_out=$(ls "$test_out_dir"/*.${out_ext} 2>/dev/null | head -1)
    if [ -z "$per_test_out" ]; then
        printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    if [ "$COMPILE_ONLY" = "true" ]; then
        printf '%s\tCOMPILE_ONLY\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    # Put each test in its own package to avoid class-name collisions when
    # batch-compiling — many tests share system names (App, Sensor, etc.)
    # that Frame emits as top-level classes. Also force a deterministic
    # file-level class name via @file:JvmName so we don't have to guess
    # kotlinc's filename→classname rules (leading digits, mixed case, etc.).
    pkg="frametest.${sanitized}"
    main_class="${pkg}.Runner"

    tmp_kt=$(mktemp)
    # @file annotations must precede `package`; `package` must precede
    # any declarations. Framec emits neither a package line nor imports,
    # so inserting both at the top of the file is safe.
    printf '@file:JvmName("Runner")\npackage %s\n\n' "$pkg" > "$tmp_kt"
    cat "$per_test_out" >> "$tmp_kt"
    mv "$tmp_kt" "$per_test_out"

    printf '%s\tRUN\t%s\t%s\n' "$test_num" "$test_name" "$main_class" >> "$MANIFEST"
    kt_files="$kt_files $per_test_out"
done

# ------------------------------------------------------------------
# Phase 2: batch compile + single-JVM dispatch
# ------------------------------------------------------------------

if [ "$COMPILE_ONLY" = "true" ]; then
    # No execution phase; still emit TAP from the manifest via the dispatcher.
    # But we don't have a compiled JAR, so just iterate the manifest directly
    # in shell for the compile-only path.
    pass=0
    fail=0
    skip=0
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
    echo "# kotlin: $pass passed, $fail failed, $skip skipped"
    exit $fail
fi

# Nothing to compile? All tests were skipped or transpile-error; dispatcher
# still runs to emit TAP for the non-RUN rows.
kt_cp=""
_libs=""
[ -f /lib/json.jar ] && _libs="/lib/json.jar"
[ -f /lib/kotlinx-coroutines-core-jvm.jar ] && {
    [ -n "$_libs" ] && _libs="${_libs}:/lib/kotlinx-coroutines-core-jvm.jar" || _libs="/lib/kotlinx-coroutines-core-jvm.jar"
}
[ -n "$_libs" ] && kt_cp="-cp $_libs"

# Batch compile with error attribution. kotlinc errors look like:
#   tmp/kotlin_out/t15_forward_parent/forward_parent.kt:10:5: error: ...
# Extract <sanitized> from the path, mark those rows, retry once.
try_kotlinc() {
    local files
    files=$(find "$COMPILE_DIR" -name "*.kt" 2>/dev/null | tr '\n' ' ')
    [ -z "$files" ] && return 0
    # -J-Xmx4g: kotlinc's default max heap (~320 MB) is exhausted by a
    # batch compile of the full test corpus (200+ .kt files) with
    # -include-runtime — the compiler OOMs holding ASTs, symbol tables,
    # and bytecode simultaneously. Bumped from 2g → 4g after the HSM
    # cascade migration added ~100 lines of generated machinery per
    # file (hsm_chain, __prepareEnter, __prepareExit, __route_to_state,
    # two cascade helpers, transition loop). At 214 test files that's
    # ~21k extra lines of bytecode the compiler holds in-memory, which
    # tipped kotlinc over the old 2g ceiling under heavy parallel
    # matrix load (host OOM-killer SIGKILL'd the JVM, marking every
    # test as `kotlinc failed`).
    # shellcheck disable=SC2086
    kotlinc -J-Xmx4g $kt_cp $files -include-runtime -d "$ALL_JAR" 2>/tmp/kotlinc_err
}

kt_mass_fail() {
    tmp_manifest="${MANIFEST}.tmp"
    awk -F'\t' 'BEGIN{OFS="\t"} {
        if ($2 == "RUN") { $2 = "COMPILE_FAIL"; $4 = "" }
        print
    }' "$MANIFEST" > "$tmp_manifest"
    mv "$tmp_manifest" "$MANIFEST"
}

if [ -n "$kt_files" ]; then
    if ! try_kotlinc; then
        # kotlinc echoes source paths with or without leading /, so match
        # on the directory-suffix regardless.
        dir_suffix="${COMPILE_DIR#/}"
        bad=$(grep -E "error:" /tmp/kotlinc_err \
                | grep -oE "${dir_suffix}/[A-Za-z0-9_]+" \
                | sed "s|${dir_suffix}/||" | sort -u)
        if [ -n "$bad" ]; then
            for s in $bad; do
                tmp_manifest="${MANIFEST}.tmp"
                awk -v s="$s" -F'\t' 'BEGIN{OFS="\t"} {
                    if ($2 == "RUN" && $4 == "frametest." s ".Runner") {
                        $2 = "COMPILE_FAIL"; $4 = ""
                    }
                    print
                }' "$MANIFEST" > "$tmp_manifest"
                mv "$tmp_manifest" "$MANIFEST"
                rm -rf "$COMPILE_DIR/${s}"
            done
            if ! try_kotlinc; then
                kt_mass_fail
                echo "# kotlinc failed even after removing bad files — see below" >&2
                head -40 /tmp/kotlinc_err >&2
            fi
        else
            kt_mass_fail
            echo "# batch kotlinc failed — see below" >&2
            head -40 /tmp/kotlinc_err >&2
        fi
    fi
fi

# Dispatch. test_runner.jar is baked into the image at /opt/test_runner.jar.
dispatcher_cp="/opt/test_runner.jar"
[ -f "$ALL_JAR" ] && dispatcher_cp="${ALL_JAR}:${dispatcher_cp}"
[ -f /lib/json.jar ] && dispatcher_cp="${dispatcher_cp}:/lib/json.jar"
[ -f /lib/kotlinx-coroutines-core-jvm.jar ] && dispatcher_cp="${dispatcher_cp}:/lib/kotlinx-coroutines-core-jvm.jar"

# Integrity check — verify dispatcher emitted test_count TAP lines.
tap_out=$(mktemp)
java -cp "$dispatcher_cp" TestRunnerKt "$MANIFEST" | tee "$tap_out"
rc=${PIPESTATUS[0]:-$?}
emitted=$(grep -cE "^(ok |not ok )" "$tap_out" || true)
rm -f "$tap_out"
if [ "$emitted" -ne "$test_count" ]; then
    echo "not ok $((test_count + 1)) - __harness_integrity__ # expected $test_count TAP lines, got $emitted"
    [ "$rc" = "0" ] && rc=1
fi
exit $rc