#!/bin/bash
# Batched Swift test runner. Each .fswift becomes a swift binary via
# parallel swiftc; then exec each. swiftc is slow per-invocation but
# parallelises across cores.

set -uo pipefail

# Source-hash cache for framec: skips re-transpile when source
# + framec version haven't changed since last run.
. /framec_cached.sh

OUTPUT="/output"
COMPILE_DIR="/tmp/swift_out"
BIN_DIR="/tmp/swift_bin"
MANIFEST="/tmp/swift_manifest.tsv"
COMPILE_ONLY="${COMPILE_ONLY:-false}"
JOBS="${SWIFT_COMPILE_JOBS:-$(nproc 2>/dev/null || echo 4)}"

target="swift"
ext="fswift"
out_ext="swift"

mkdir -p "$OUTPUT"
rm -rf "$COMPILE_DIR" "$BIN_DIR" "$MANIFEST" 2>/dev/null
mkdir -p "$COMPILE_DIR" "$BIN_DIR"
: > "$MANIFEST"

tests=$(find /tests/common/positive -name "*.$ext" 2>/dev/null | sort)
lang_tests=$(find /tests/swift -name "*.$ext" 2>/dev/null | sort)
if [ -n "$lang_tests" ]; then
    tests="$tests
$lang_tests"
fi

test_count=$(echo "$tests" | grep -c . || echo 0)
if [ "$test_count" -eq 0 ]; then
    echo "TAP version 14"
    echo "1..0 # SKIP no swift tests found"
    exit 0
fi

echo "TAP version 14"
echo "1..$test_count"

test_num=0
COMPILE_LIST="/tmp/swift_compile.list"
: > "$COMPILE_LIST"

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

    src=$(ls "$test_src_dir"/*.swift 2>/dev/null | head -1)
    if [ -z "$src" ]; then
        printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    if [ "$COMPILE_ONLY" = "true" ]; then
        printf '%s\tCOMPILE_ONLY\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    bin_path="$BIN_DIR/${sanitized}"
    printf '%s\t%s\n' "$src" "$bin_path" >> "$COMPILE_LIST"
    printf '%s\tRUN\t%s\t%s\n' "$test_num" "$test_name" "$sanitized" >> "$MANIFEST"
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
    echo "# swift: $pass passed, $fail failed, $skip skipped"
    exit $fail
fi

STATUS_DIR="/tmp/swift_compile_status"
rm -rf "$STATUS_DIR" 2>/dev/null
mkdir -p "$STATUS_DIR"
export STATUS_DIR

compile_one() {
    local src="$1"
    local bin="$2"
    local name
    name=$(basename "$bin")
    if swiftc -Onone -o "$bin" "$src" 2> "$STATUS_DIR/${name}.err"; then
        echo 0 > "$STATUS_DIR/${name}.rc"
    else
        echo 1 > "$STATUS_DIR/${name}.rc"
    fi
}
export -f compile_one

if [ -s "$COMPILE_LIST" ]; then
    awk -F'\t' '{print $1; print $2}' "$COMPILE_LIST" | \
        xargs -n 2 -P "$JOBS" bash -c 'compile_one "$@"' _
fi

tmp_manifest="${MANIFEST}.tmp"
awk -v sd="$STATUS_DIR" -F'\t' 'BEGIN{OFS="\t"} {
    if ($2 == "RUN") {
        rc_file = sd "/" $4 ".rc"
        getline rc < rc_file; close(rc_file)
        if (rc != "0") { $2 = "COMPILE_FAIL"; $4 = "" }
    }
    print
}' "$MANIFEST" > "$tmp_manifest"
mv "$tmp_manifest" "$MANIFEST"

TIMEOUT_SEC="${SWIFT_TEST_TIMEOUT:-30}"
EXEC_DIR="/tmp/swift_exec_status"
rm -rf "$EXEC_DIR" 2>/dev/null
mkdir -p "$EXEC_DIR"
export EXEC_DIR BIN_DIR TIMEOUT_SEC

exec_one() {
    local sanitized="$1"
    local bin_path="$BIN_DIR/$sanitized"
    if [ ! -x "$bin_path" ]; then
        echo 127 > "$EXEC_DIR/${sanitized}.rc"
        echo "binary missing" > "$EXEC_DIR/${sanitized}.out"
        return
    fi
    # setsid --wait + sync — defends against partial-read flakes
    # under heavy parallel matrix load (xargs -P × 17 containers).
    # Without --wait, the classifier in the main loop occasionally
    # read a partial .out and reported "unrecognized output" as a
    # false failure. Same pattern as go/dart/gdscript/c batch scripts
    # (matrix_flake_fix_2026_04_26 + this extension to swift).
    setsid --wait timeout "$TIMEOUT_SEC" "$bin_path" \
        > "$EXEC_DIR/${sanitized}.out" 2>&1
    sync "$EXEC_DIR/${sanitized}.out" 2>/dev/null || true
    echo $? > "$EXEC_DIR/${sanitized}.rc"
}
export -f exec_one

awk -F'\t' '$2 == "RUN" { print $4 }' "$MANIFEST" | \
    xargs -n 1 -P "$JOBS" -I{} bash -c 'exec_one "$@"' _ {}

pass=0; fail=0; skip=0
while IFS=$'\t' read -r num status name rest; do
    IFS=$'\t' read -r bin extra <<< "$rest"
    case "$status" in
        SKIP)
            echo "ok $num - $name # SKIP"; skip=$((skip+1)) ;;
        TRANSPILE_ERROR_OK)
            echo "ok $num - $name # correctly rejected by transpiler"; pass=$((pass+1)) ;;
        TRANSPILE_FAIL)
            echo "not ok $num - $name # transpile failed"; fail=$((fail+1)) ;;
        NO_OUTPUT)
            echo "not ok $num - $name # no output file"; fail=$((fail+1)) ;;
        COMPILE_FAIL)
            echo "not ok $num - $name # swiftc failed"; fail=$((fail+1)) ;;
        RUN)
            rc_file="$EXEC_DIR/${bin}.rc"
            out_file="$EXEC_DIR/${bin}.out"
            if [ ! -f "$rc_file" ]; then
                echo "not ok $num - $name # not executed"; fail=$((fail+1)); continue
            fi
            code=$(cat "$rc_file")
            out=$(cat "$out_file" 2>/dev/null)
            if [ "$code" = "124" ]; then
                echo "not ok $num - $name # TIMEOUT"; fail=$((fail+1))
            elif [ "$code" != "0" ]; then
                echo "not ok $num - $name # runtime error (exit $code)"
                echo "$out" | head -5 | sed 's/^/  # /'
                fail=$((fail+1))
            elif echo "$out" | grep -q "^not ok "; then
                echo "not ok $num - $name"; fail=$((fail+1))
            elif echo "$out" | grep -qE "^ok |PASS"; then
                echo "ok $num - $name"; pass=$((pass+1))
            elif [ -z "$out" ]; then
                echo "ok $num - $name # clean exit"; pass=$((pass+1))
            else
                # Defensive re-read: under heavy parallel matrix load
                # the .out file occasionally reads mid-write despite
                # setsid --wait + sync (Docker volume page-cache
                # propagation). Re-cat after a brief settle and check
                # again — if recognizable, treat as PASS. Same pattern
                # as go/dart/gdscript/c batch scripts.
                sleep 0.1
                out=$(cat "$out_file" 2>/dev/null)
                if echo "$out" | grep -qE "^ok |PASS"; then
                    echo "ok $num - $name"; pass=$((pass+1))
                elif echo "$out" | grep -q "^not ok "; then
                    echo "not ok $num - $name"; fail=$((fail+1))
                else
                    echo "not ok $num - $name # unrecognized output"
                    echo "$out" | head -3 | sed 's/^/  # /'
                    fail=$((fail+1))
                fi
            fi ;;
        *)
            echo "not ok $num - $name # unknown status $status"; fail=$((fail+1)) ;;
    esac
done < "$MANIFEST"

# Integrity check — pass+fail+skip must equal declared plan count. Catches
# silent dispatcher crashes / missing rows in the manifest.
if [ "$((pass + fail + skip))" -ne "$test_count" ]; then
    echo "not ok $((test_count + 1)) - __harness_integrity__ # expected $test_count results, got $((pass + fail + skip))"
    fail=$((fail + 1))
fi


echo ""
echo "# swift: $pass passed, $fail failed, $skip skipped"
exit $fail
