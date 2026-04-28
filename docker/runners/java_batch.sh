#!/bin/bash
# Batched Java test runner. Same shape as kotlin_batch.sh:
#   1. Transpile every .fjava to .java under /tmp/java_src/<sanitized>/,
#      prepending `package frametest.<sanitized>;` so tests with identical
#      system/class names (App, Sensor, Main …) don't collide.
#   2. One javac invocation compiles everything into /tmp/java_out.
#   3. /opt/test_runner.jar (pre-baked TestRunner) iterates the manifest
#      and reflectively invokes `frametest.<sanitized>.Main.main()` per
#      test inside a single JVM.

set -uo pipefail

# Source-hash cache for framec: skips re-transpile when source
# + framec version haven't changed since last run.
. /framec_cached.sh

OUTPUT="/output"
SRC_ROOT="/tmp/java_src"
CLASSES_DIR="/tmp/java_classes"
MANIFEST="/tmp/java_manifest.tsv"
COMPILE_ONLY="${COMPILE_ONLY:-false}"

target="java"
ext="fjava"
out_ext="java"

mkdir -p "$OUTPUT"
rm -rf "$SRC_ROOT" "$CLASSES_DIR" "$MANIFEST" 2>/dev/null
mkdir -p "$SRC_ROOT" "$CLASSES_DIR"
: > "$MANIFEST"

tests=$(find /tests/common/positive -name "*.$ext" 2>/dev/null | sort)
# Exclude /tests/java/multi/ — those are processed by the multi-source
# sweep below as one logical TAP test per directory.
lang_tests=$(find /tests/java -name "*.$ext" -not -path '*/multi/*' 2>/dev/null | sort)
if [ -n "$lang_tests" ]; then
    tests="$tests
$lang_tests"
fi

# Multi-source cases: each tests/java/multi/<case>/ directory is one
# logical test that contains N .fjava files (one @@system each, since
# Java requires one public class per file) plus a Main.java driver
# with `public static void main(String[] args)`. All N+1 sources land
# in the same generated package so they can call each other without
# qualification.
multi_dirs=$(find /tests/java/multi -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)
multi_count=$(echo "$multi_dirs" | grep -c . || echo 0)
single_count=$(echo "$tests" | grep -c . || echo 0)
test_count=$((single_count + multi_count))
if [ "$test_count" -eq 0 ]; then
    echo "TAP version 14"
    echo "1..0 # SKIP no java tests found"
    exit 0
fi

echo "TAP version 14"
echo "1..$test_count"

test_num=0
java_files=""

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
    pkg="frametest.${sanitized}"
    test_src_dir="$SRC_ROOT/${sanitized}"
    rm -rf "$test_src_dir" 2>/dev/null
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

    # framec emits one .java named after the public class. There should be
    # exactly one; take the first.
    src_java=$(ls "$test_src_dir"/*.java 2>/dev/null | head -1)
    if [ -z "$src_java" ]; then
        printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    if [ "$COMPILE_ONLY" = "true" ]; then
        printf '%s\tCOMPILE_ONLY\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    # Prepend package declaration. The transpiler emits `import java.util.*;`
    # on line 1 of some files — Java requires `package` BEFORE any import,
    # so we splice it in at the top.
    tmp_java=$(mktemp)
    printf 'package %s;\n\n' "$pkg" > "$tmp_java"
    cat "$src_java" >> "$tmp_java"
    mv "$tmp_java" "$src_java"

    # Framec emits a non-public `class Main { public static void main }`
    # alongside the public system class. The TestRunner dispatches to
    # that Main class in the test's package.
    main_class="${pkg}.Main"
    printf '%s\tRUN\t%s\t%s\n' "$test_num" "$test_name" "$main_class" >> "$MANIFEST"
    java_files="$java_files $src_java"
done

# ---- Multi-source sweep ----
# Each tests/java/multi/<case>/ dir is one logical TAP test. The dir
# contains N .fjava sources (one @@system each → one public class per
# file) plus a Main.java driver. We transpile each .fjava, prepend
# the package declaration to every .java in the dir (incl. Main.java),
# and let the batch javac downstream pick them all up.
for case_dir in $multi_dirs; do
    test_num=$((test_num + 1))
    case_name=$(basename "$case_dir")

    # Per-case @@skip in any .fjava skips the whole dir.
    if grep -q "@@skip\|@skip" "$case_dir"/*.fjava 2>/dev/null; then
        printf '%s\tSKIP\t%s\n' "$test_num" "$case_name" >> "$MANIFEST"
        continue
    fi

    sanitized="t${test_num}_$(printf '%s' "$case_name" | sed 's/[^A-Za-z0-9_]/_/g')"
    pkg="frametest.${sanitized}"
    test_src_dir="$SRC_ROOT/${sanitized}"
    rm -rf "$test_src_dir" 2>/dev/null
    mkdir -p "$test_src_dir"

    transpile_failed=false
    for fjava in "$case_dir"/*.fjava; do
        [ -f "$fjava" ] || continue
        tmp_out=$(mktemp -d)
        if ! framec_cached "$target" "$tmp_out" "$fjava" /tmp/compile_err; then
            err_line=$(head -5 /tmp/compile_err 2>/dev/null | tr '\n' '\\' | sed 's/\\$//' | sed 's/\\/\\n/g')
            printf '%s\tTRANSPILE_FAIL\t%s\t\t%s\n' "$test_num" "$case_name" "$err_line" >> "$MANIFEST"
            transpile_failed=true
            break
        fi
        # framec emits exactly one .java per .fjava, named after the
        # public class. Move it into the case's package dir.
        out_java=$(ls "$tmp_out"/*.java 2>/dev/null | head -1)
        if [ -z "$out_java" ]; then
            printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$case_name" >> "$MANIFEST"
            transpile_failed=true
            break
        fi
        mv "$out_java" "$test_src_dir/"
    done
    if [ "$transpile_failed" = "true" ]; then
        continue
    fi

    # Driver: <case>/Main.java is required. Copy as-is — we will
    # prepend the package declaration in the unified pass below.
    if [ ! -f "$case_dir/Main.java" ]; then
        printf '%s\tNO_DRIVER\t%s\n' "$test_num" "$case_name" >> "$MANIFEST"
        continue
    fi
    cp "$case_dir/Main.java" "$test_src_dir/Main.java"

    if [ "$COMPILE_ONLY" = "true" ]; then
        printf '%s\tCOMPILE_ONLY\t%s\n' "$test_num" "$case_name" >> "$MANIFEST"
    fi

    # Prepend `package <pkg>;` to every .java in the case dir.
    # Strip any leading `package ...;` line the driver may already
    # have (a hand-written Main.java is allowed to declare one for
    # standalone editor use, but ours overrides for matrix isolation).
    for j in "$test_src_dir"/*.java; do
        [ -f "$j" ] || continue
        tmp_java=$(mktemp)
        # Strip any existing package declaration on line 1.
        if head -1 "$j" | grep -qE '^[[:space:]]*package[[:space:]]'; then
            tail -n +2 "$j" > "$tmp_java.body"
        else
            cp "$j" "$tmp_java.body"
        fi
        printf 'package %s;\n\n' "$pkg" > "$tmp_java"
        cat "$tmp_java.body" >> "$tmp_java"
        mv "$tmp_java" "$j"
        rm -f "$tmp_java.body"
        java_files="$java_files $j"
    done

    main_class="${pkg}.Main"
    printf '%s\tRUN\t%s\t%s\n' "$test_num" "$case_name" "$main_class" >> "$MANIFEST"
done

if [ "$COMPILE_ONLY" = "true" ]; then
    pass=0; fail=0; skip=0
    while IFS=$'\t' read -r num status name rest; do
        case "$status" in
            SKIP)                   echo "ok $num - $name # SKIP";                              skip=$((skip+1)) ;;
            TRANSPILE_ERROR_OK)     echo "ok $num - $name # correctly rejected by transpiler";  pass=$((pass+1)) ;;
            TRANSPILE_FAIL)         echo "not ok $num - $name # transpile failed";              fail=$((fail+1)) ;;
            NO_OUTPUT)              echo "not ok $num - $name # no output file";                fail=$((fail+1)) ;;
            NO_DRIVER)              echo "not ok $num - $name # multi-source case missing Main.java"; fail=$((fail+1)) ;;
            COMPILE_ONLY|RUN)       echo "ok $num - $name # transpiled";                        pass=$((pass+1)) ;;
        esac
    done < "$MANIFEST"
    echo ""
    echo "# java: $pass passed, $fail failed, $skip skipped"
    exit $fail
fi

# Batch compile. -Xmaxerrs huge so javac doesn't stop early — we want
# all errors so we can attribute to the right tests. On failure, scrape
# error-line paths, mark those tests as COMPILE_FAIL, remove their
# sources, retry. C# follows the same pattern.
compile_cp="$CLASSES_DIR"
[ -f /lib/json.jar ] && compile_cp="$CLASSES_DIR:/lib/json.jar"

try_javac() {
    local files
    files=$(find "$SRC_ROOT" -name "*.java" 2>/dev/null | tr '\n' ' ')
    [ -z "$files" ] && return 0
    # shellcheck disable=SC2086
    javac -Xmaxerrs 1000 -cp "$compile_cp" -d "$CLASSES_DIR" $files 2>/tmp/javac_err
}

mass_mark_fail() {
    tmp_manifest="${MANIFEST}.tmp"
    awk -F'\t' 'BEGIN{OFS="\t"} {
        if ($2 == "RUN") { $2 = "COMPILE_FAIL"; $4 = "" }
        print
    }' "$MANIFEST" > "$tmp_manifest"
    mv "$tmp_manifest" "$MANIFEST"
}

if [ -n "$java_files" ]; then
    if ! try_javac; then
        bad=$(grep -E ":[0-9]+: error" /tmp/javac_err \
                | grep -oE "$SRC_ROOT/[A-Za-z0-9_]+" \
                | sed "s|$SRC_ROOT/||" | sort -u)
        if [ -n "$bad" ]; then
            for s in $bad; do
                tmp_manifest="${MANIFEST}.tmp"
                awk -v s="$s" -F'\t' 'BEGIN{OFS="\t"} {
                    if ($2 == "RUN" && $4 == "frametest." s ".Main") {
                        $2 = "COMPILE_FAIL"; $4 = ""
                    }
                    print
                }' "$MANIFEST" > "$tmp_manifest"
                mv "$tmp_manifest" "$MANIFEST"
                rm -rf "$SRC_ROOT/${s}"
            done
            if ! try_javac; then
                mass_mark_fail
                echo "# javac failed even after removing bad files — see below" >&2
                head -40 /tmp/javac_err >&2
            fi
        else
            mass_mark_fail
            echo "# batch javac failed — see below" >&2
            head -40 /tmp/javac_err >&2
        fi
    fi
fi

run_cp="$CLASSES_DIR:/opt/test_runner.jar"
[ -f /lib/json.jar ] && run_cp="${run_cp}:/lib/json.jar"

# Integrity check — verify dispatcher emitted test_count TAP lines.
tap_out=$(mktemp)
java -cp "$run_cp" TestRunner "$MANIFEST" | tee "$tap_out"
rc=${PIPESTATUS[0]:-$?}
emitted=$(grep -cE "^(ok |not ok )" "$tap_out" || true)
rm -f "$tap_out"
if [ "$emitted" -ne "$test_count" ]; then
    echo "not ok $((test_count + 1)) - __harness_integrity__ # expected $test_count TAP lines, got $emitted"
    [ "$rc" = "0" ] && rc=1
fi
exit $rc