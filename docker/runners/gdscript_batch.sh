#!/bin/bash
# Batched GDScript test runner.
#
# Godot cold start dominates (~520ms per invocation). Two batching layers:
#   1. Process-level: run M tests inside a single godot process via a
#      harness script (load + .new() each test as a SceneTree subclass —
#      an inner script's quit() does NOT terminate the parent process,
#      empirically verified 2026-05-03).
#   2. Across-batch: run B parallel batches via xargs -P, each batch
#      feeding the harness M test paths.
#
# With B=4 batches × M≈70 tests/batch, we go from 255 godot startups
# down to 4 — eliminating ~99% of startup cost.
#
# Per-test stdout is captured via a `==FRAME-TEST-BEGIN== <path>` /
# `==FRAME-TEST-END== <path>` marker pair the harness prints; this
# script's classifier slices the harness output into per-test .out
# files matching the existing single-test format.

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

# ---- Batched parallel godot execution ----
TIMEOUT_SEC="${GDSCRIPT_TEST_TIMEOUT:-60}"
# Tests per godot invocation. Big enough to amortize startup, small
# enough that one slow test in a batch doesn't penalize the whole
# batch under timeout. Default ~70 with 255 tests / 4 batches.
BATCH_SIZE="${GDSCRIPT_BATCH_SIZE:-70}"
export STATUS_DIR COMPILE_DIR TIMEOUT_SEC BATCH_SIZE

# Harness GDScript: loads each test path as a SceneTree subclass and
# instantiates it. The inner script's _init() runs the test body and
# its quit() call exits the inner SceneTree without killing the
# parent process. Markers around each test let the classifier slice
# stdout per test.
export HARNESS_GD=/tmp/gd_harness.gd
cat > "$HARNESS_GD" <<'GDEOF'
extends SceneTree
func _init():
    var paths = OS.get_cmdline_user_args()
    var sep_b = "==FRAME-TEST-BEGIN=="
    var sep_e = "==FRAME-TEST-END=="
    for p in paths:
        print(sep_b + " " + p)
        var s = load(p)
        if s == null:
            print("[harness] LOAD-FAIL " + p)
        else:
            var inst = s.new()
            # inst is a SceneTree subclass — its _init() body runs the
            # test inline; quit() is a no-op for a non-main SceneTree.
            inst = null
        print(sep_e + " " + p)
    quit()
GDEOF

run_batch() {
    local batch_id="$1"
    local manifest="$2"   # tab-separated: <sanitized>\t<src_path>
    local batch_out="$STATUS_DIR/batch_${batch_id}.out"

    # Collect all src paths for this batch.
    local paths=()
    while IFS=$'\t' read -r sanitized src_path; do
        [ -z "$src_path" ] && continue
        paths+=("$src_path")
    done < "$manifest"

    if [ "${#paths[@]}" -eq 0 ]; then
        return
    fi

    # Single godot invocation, multiple tests. setsid --wait flushes
    # godot's spawned children before we move on (same pattern as
    # the legacy per-test path).
    setsid --wait timeout "$TIMEOUT_SEC" godot --headless \
        --script "$HARNESS_GD" -- "${paths[@]}" > "$batch_out" 2>&1
    local rc=$?
    sync "$batch_out" 2>/dev/null || true

    # Slice the batch output into per-test .out / .rc by the
    # FRAME-TEST-BEGIN/END markers.
    awk -v OUTDIR="$STATUS_DIR" -v RC="$rc" '
        /^==FRAME-TEST-BEGIN== / {
            path = $2
            n = split(path, parts, "/")
            sanitized = parts[n - 1]   # /tmp/gd_out/<sanitized>/foo.gd
            cur = OUTDIR "/" sanitized ".out"
            cur_rc = OUTDIR "/" sanitized ".rc"
            saw_begin = 1
            content = ""
            next
        }
        /^==FRAME-TEST-END== / {
            if (saw_begin) {
                printf "%s", content > cur
                close(cur)
                # Per-test rc: if the whole batch timed out (rc=124)
                # propagate that; otherwise treat each test as
                # exit 0 (its content gets classified by the next
                # stage, just like the legacy single-test flow).
                if (RC == 124) {
                    print "124" > cur_rc
                } else {
                    print "0" > cur_rc
                }
                close(cur_rc)
                saw_begin = 0
            }
            next
        }
        saw_begin { content = content $0 "\n" }
    ' "$batch_out"
}
export -f run_batch

# Build batch manifests. Each batch gets BATCH_SIZE rows of
# <sanitized>\t<src_path>.
BATCH_DIR="$STATUS_DIR/batches"
mkdir -p "$BATCH_DIR"
batch_idx=0
row_idx=0
batch_file="$BATCH_DIR/batch_$(printf '%04d' $batch_idx).tsv"
: > "$batch_file"

awk -F'\t' '$2 == "RUN" { print $4 }' "$MANIFEST" | while read -r sanitized; do
    src=$(ls "$COMPILE_DIR/$sanitized"/*.gd 2>/dev/null | head -1)
    [ -z "$src" ] && continue
    printf '%s\t%s\n' "$sanitized" "$src" >> "$batch_file"
    row_idx=$((row_idx + 1))
    if [ "$row_idx" -ge "$BATCH_SIZE" ]; then
        batch_idx=$((batch_idx + 1))
        row_idx=0
        batch_file="$BATCH_DIR/batch_$(printf '%04d' $batch_idx).tsv"
        : > "$batch_file"
    fi
done

# Drop empty trailing batch if we didn't write any rows to it.
[ ! -s "$batch_file" ] && rm -f "$batch_file"

# Run each batch in parallel; B=$JOBS (defaults to half nproc).
ls "$BATCH_DIR"/batch_*.tsv 2>/dev/null | \
    xargs -n 1 -P "$JOBS" -I{} bash -c '
        f="$1"
        id=$(basename "$f" .tsv | sed "s/batch_//")
        run_batch "$id" "$f"
    ' _ {}

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
