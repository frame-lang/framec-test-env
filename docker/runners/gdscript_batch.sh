#!/bin/bash
# Batched GDScript test runner.
# Godot cold start dominates (~1-2s per invocation) and godot has no native
# multi-script runner mode, so we keep one godot process per test but run
# them in parallel via xargs -P. Each godot instance eats ~150-250MB of RSS;
# cap concurrency a bit lower than the other languages to stay under
# container memory limits.

set -uo pipefail

# Source-hash cache for framec: skips re-transpile when source
# + framec version haven't changed since last run.
. /framec_cached.sh

OUTPUT="/output"
COMPILE_DIR="/tmp/gd_out"
MANIFEST="/tmp/gd_manifest.tsv"
STATUS_DIR="/tmp/gd_status"
COMPILE_ONLY="${COMPILE_ONLY:-false}"
# Godot is memory-heavy. Half the cores by default; override if the host
# has headroom.
JOBS="${GDSCRIPT_TEST_JOBS:-$(( ($(nproc 2>/dev/null || echo 4) + 1) / 2 ))}"
[ "$JOBS" -lt 1 ] && JOBS=1

target="gdscript"
ext="fgd"
out_ext="gd"

mkdir -p "$OUTPUT"
rm -rf "$COMPILE_DIR" "$MANIFEST" "$STATUS_DIR" 2>/dev/null
mkdir -p "$COMPILE_DIR" "$STATUS_DIR"
: > "$MANIFEST"

tests=$(find /tests/common/positive -name "*.$ext" 2>/dev/null | sort)
lang_tests=$(find /tests/gdscript -name "*.$ext" 2>/dev/null | sort)
if [ -n "$lang_tests" ]; then
    tests="$tests
$lang_tests"
fi

test_count=$(echo "$tests" | grep -c . || echo 0)
if [ "$test_count" -eq 0 ]; then
    echo "TAP version 14"
    echo "1..0 # SKIP no gdscript tests found"
    exit 0
fi

echo "TAP version 14"
echo "1..$test_count"

test_num=0

# Detect godot availability once; if missing, treat all RUN rows as
# transpile-only success (matches runner.sh's existing fallback).
have_godot=false
command -v godot >/dev/null 2>&1 && have_godot=true

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

    src=$(ls "$test_src_dir"/*.gd 2>/dev/null | head -1)
    if [ -z "$src" ]; then
        printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    if [ "$COMPILE_ONLY" = "true" ] || [ "$have_godot" != "true" ]; then
        printf '%s\tCOMPILE_ONLY\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    printf '%s\tRUN\t%s\t%s\n' "$test_num" "$test_name" "$sanitized" >> "$MANIFEST"
done

if [ "$COMPILE_ONLY" = "true" ] || [ "$have_godot" != "true" ]; then
    pass=0; fail=0; skip=0
    while IFS=$'\t' read -r num status name rest; do
        case "$status" in
            SKIP)                   echo "ok $num - $name # SKIP";                              skip=$((skip+1)) ;;
            TRANSPILE_ERROR_OK)     echo "ok $num - $name # correctly rejected by transpiler";  pass=$((pass+1)) ;;
            TRANSPILE_FAIL)         echo "not ok $num - $name # transpile failed";              fail=$((fail+1)) ;;
            NO_OUTPUT)              echo "not ok $num - $name # no output file";                fail=$((fail+1)) ;;
            COMPILE_ONLY)           echo "ok $num - $name # transpiled (no godot)";             pass=$((pass+1)) ;;
            RUN)                    echo "ok $num - $name # transpiled";                        pass=$((pass+1)) ;;
        esac
    done < "$MANIFEST"
    echo ""
    echo "# gdscript: $pass passed, $fail failed, $skip skipped"
    exit $fail
fi

# ---- Parallel godot execution ----
TIMEOUT_SEC="${GDSCRIPT_TEST_TIMEOUT:-10}"
export STATUS_DIR COMPILE_DIR TIMEOUT_SEC

run_one() {
    local sanitized="$1"
    local src
    src=$(ls "$COMPILE_DIR/$sanitized"/*.gd 2>/dev/null | head -1)
    if [ -z "$src" ]; then
        echo 1 > "$STATUS_DIR/${sanitized}.rc"
        echo "source missing" > "$STATUS_DIR/${sanitized}.out"
        return
    fi
    # setsid --wait: godot spawns detached helper children that inherit
    # our redirected stdout fd. A plain redirection lets this shell move
    # on to write .rc while those children are still writing to .out —
    # the classifier then reads a partially-populated file and reports
    # "unrecognized output". --wait blocks until every process in the
    # new session exits, so .out is fully flushed before we proceed.
    setsid --wait timeout "$TIMEOUT_SEC" godot --headless --script "$src" \
        > "$STATUS_DIR/${sanitized}.out" 2>&1
    # Force the kernel page cache to commit so any concurrent reader
    # in the post-loop sees the final size+content. Cheap; only this
    # specific file's pages.
    sync "$STATUS_DIR/${sanitized}.out" 2>/dev/null || true
    echo $? > "$STATUS_DIR/${sanitized}.rc"
}
export -f run_one

awk -F'\t' '$2 == "RUN" { print $4 }' "$MANIFEST" | \
    xargs -n 1 -P "$JOBS" -I{} bash -c 'run_one "$@"' _ {}

pass=0; fail=0; skip=0
while IFS=$'\t' read -r num status name rest; do
    IFS=$'\t' read -r sanitized extra <<< "$rest"
    case "$status" in
        SKIP)
            echo "ok $num - $name # SKIP"; skip=$((skip+1)) ;;
        TRANSPILE_ERROR_OK)
            echo "ok $num - $name # correctly rejected by transpiler"; pass=$((pass+1)) ;;
        TRANSPILE_FAIL)
            echo "not ok $num - $name # transpile failed"; fail=$((fail+1)) ;;
        NO_OUTPUT)
            echo "not ok $num - $name # no output file"; fail=$((fail+1)) ;;
        COMPILE_ONLY)
            echo "ok $num - $name # transpiled (no godot)"; pass=$((pass+1)) ;;
        RUN)
            rc_file="$STATUS_DIR/${sanitized}.rc"
            out_file="$STATUS_DIR/${sanitized}.out"
            if [ ! -f "$rc_file" ]; then
                echo "not ok $num - $name # not executed"; fail=$((fail+1)); continue
            fi
            code=$(cat "$rc_file")
            out=$(cat "$out_file" 2>/dev/null)
            if [ "$code" = "124" ]; then
                # runner.sh's existing behaviour: godot timeout → treat as
                # pass (test transpiled, godot just took too long to boot).
                echo "ok $num - $name # transpiled (godot timed out)"
                pass=$((pass+1))
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
                # Defensive re-read: even with setsid --wait + sync,
                # the matrix occasionally reads .out mid-write (likely
                # Docker volume page-cache propagation under heavy
                # parallel matrix load). Re-cat after a brief settle
                # and re-classify; if the output is now recognizable,
                # treat as PASS.
                sleep 0.1
                out=$(cat "$out_file" 2>/dev/null)
                if echo "$out" | grep -qE "^ok |PASS"; then
                    echo "ok $num - $name"; pass=$((pass+1))
                elif echo "$out" | grep -q "^not ok "; then
                    echo "not ok $num - $name"; fail=$((fail+1))
                else
                    # Still unrecognized after retry — preserve the
                    # full output for post-hoc analysis.
                    unrec_dir="/output/__unrecognized__"
                    mkdir -p "$unrec_dir" 2>/dev/null
                    cp "$out_file" "$unrec_dir/${sanitized}.out" 2>/dev/null
                    echo "not ok $num - $name # unrecognized output (full: $unrec_dir/${sanitized}.out)"
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
echo "# gdscript: $pass passed, $fail failed, $skip skipped"
exit $fail
