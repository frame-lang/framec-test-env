#!/bin/bash
# Batched Go test runner.
#
# Each test is a standalone `package main` file. Instead of invoking
# `go build` per test (each pays ~30-100ms toolchain overhead even
# with a warm cache), we lay out all tests as separate sub-packages
# under a single Go module and run ONE `go build ./cmd/...`. The Go
# toolchain parallelizes the builds internally and amortizes startup
# across the whole corpus.
#
# Layout:
#   /go_runner/go.mod                (pre-created at image build)
#   /go_runner/cmd/<sanitized>/main.go    (one per test)
#   /go_runner/bin/<sanitized>            (output binaries)

set -uo pipefail

# Source-hash cache for framec: skips re-transpile when source
# + framec version haven't changed since last run.
. /framec_cached.sh

OUTPUT="/output"
COMPILE_DIR="/tmp/go_out"
RUNNER_ROOT="/go_runner"
CMD_DIR="$RUNNER_ROOT/cmd"
BIN_DIR="$RUNNER_ROOT/bin"
MANIFEST="/tmp/go_manifest.tsv"
COMPILE_ONLY="${COMPILE_ONLY:-false}"
JOBS="${GO_COMPILE_JOBS:-$(nproc 2>/dev/null || echo 4)}"

target="go"
ext="fgo"
out_ext="go"

mkdir -p "$OUTPUT"
rm -rf "$COMPILE_DIR" "$CMD_DIR" "$BIN_DIR" "$MANIFEST" 2>/dev/null
mkdir -p "$COMPILE_DIR" "$CMD_DIR" "$BIN_DIR"
: > "$MANIFEST"

tests=$(find /tests/common/positive -name "*.$ext" 2>/dev/null | sort)
lang_tests=$(find /tests/go -name "*.$ext" 2>/dev/null | sort)
if [ -n "$lang_tests" ]; then
    tests="$tests
$lang_tests"
fi

test_count=$(echo "$tests" | grep -c . || echo 0)
if [ "$test_count" -eq 0 ]; then
    echo "TAP version 14"
    echo "1..0 # SKIP no go tests found"
    exit 0
fi

echo "TAP version 14"
echo "1..$test_count"

test_num=0
COMPILE_LIST="/tmp/go_compile.list"
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

    src=$(ls "$test_src_dir"/*.go 2>/dev/null | grep -v "_test\.go$" | head -1)
    if [ -z "$src" ]; then
        # Fall back to any .go (the old runner renames _test.go variants)
        src=$(ls "$test_src_dir"/*.go 2>/dev/null | head -1)
    fi
    if [ -z "$src" ]; then
        printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    # `go build` rejects files named *_test.go outside of a test context.
    if echo "$src" | grep -q '_test\.go$'; then
        renamed="${src%_test.go}_run.go"
        cp "$src" "$renamed"
        src="$renamed"
    fi

    if [ "$COMPILE_ONLY" = "true" ]; then
        printf '%s\tCOMPILE_ONLY\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    # Lay out as a sub-package: /go_runner/cmd/<sanitized>/main.go
    pkg_dir="$CMD_DIR/$sanitized"
    mkdir -p "$pkg_dir"
    cp "$src" "$pkg_dir/main.go"
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
    echo "# go: $pass passed, $fail failed, $skip skipped"
    exit $fail
fi

STATUS_DIR="/tmp/go_compile_status"
rm -rf "$STATUS_DIR" 2>/dev/null
mkdir -p "$STATUS_DIR"

# Single multi-bin go build. The Go toolchain parallelizes
# internally, so xargs -P is unnecessary here.
BUILD_LOG="$STATUS_DIR/go_build.log"
( cd "$RUNNER_ROOT" && go build -o "$BIN_DIR/" ./cmd/... ) > "$BUILD_LOG" 2>&1
build_rc=$?

# If the build failed, scrape per-package errors to mark
# specific tests COMPILE_FAIL. Errors look like:
#   ./cmd/<sanitized>/main.go:NN:CC: ...message
# Falls back to marking everything COMPILE_FAIL if we can't
# attribute (preserves the integrity-check invariant).
if [ "$build_rc" -ne 0 ]; then
    bad=$(grep -oE 'cmd/[A-Za-z0-9_]+/' "$BUILD_LOG" | sed 's|cmd/||;s|/||' | sort -u)
    if [ -n "$bad" ]; then
        # Retry build excluding the bad packages — some otherwise-good
        # tests may still need compilation. Each retry is cheap because
        # Go caches per-package.
        for s in $bad; do
            rm -rf "$CMD_DIR/$s"
        done
        ( cd "$RUNNER_ROOT" && go build -o "$BIN_DIR/" ./cmd/... ) >> "$BUILD_LOG" 2>&1 || true
    fi
fi

# Mark RUN rows whose binary doesn't exist as COMPILE_FAIL.
tmp_manifest="${MANIFEST}.tmp"
awk -v bd="$BIN_DIR" -F'\t' 'BEGIN{OFS="\t"} {
    if ($2 == "RUN") {
        bin = bd "/" $4
        cmd = "test -x \"" bin "\""
        if (system(cmd) != 0) { $2 = "COMPILE_FAIL"; $4 = "" }
    }
    print
}' "$MANIFEST" > "$tmp_manifest"
mv "$tmp_manifest" "$MANIFEST"

TIMEOUT_SEC="${GO_TEST_TIMEOUT:-30}"
EXEC_DIR="/tmp/go_exec_status"
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
    # setsid --wait guarantees that even if the binary spawned any
    # background goroutine writers (uncommon for Frame state-machine
    # tests but defensive), all of them have closed their stdout fd
    # before we proceed to write the .rc file. Without --wait, the
    # classifier in the main loop occasionally reads a partial .out
    # under heavy parallel matrix load (xargs -P × 17 containers),
    # mistakes it for "unrecognized output", and reports a false
    # failure. Same pattern dart_batch.sh adopted in 2026-04-24.
    setsid --wait timeout "$TIMEOUT_SEC" "$bin_path" \
        > "$EXEC_DIR/${sanitized}.out" 2>&1
    # Force the kernel page cache to commit so any concurrent reader
    # sees the final size+content, not a stale cached prefix.
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
            echo "not ok $num - $name # go build failed"
            [ -f "$STATUS_DIR/${name}.err" ] && head -3 "$STATUS_DIR/${name}.err" | sed 's/^/  # /'
            fail=$((fail+1)) ;;
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
                # the .out file occasionally read mid-write despite
                # setsid --wait + sync (likely Docker volume page-cache
                # propagation). Re-cat after a brief settle and check
                # again — if the output is now recognizable, treat as
                # PASS. Cost is bounded (≤200ms × number-of-flaky-cases
                # per matrix run).
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
echo "# go: $pass passed, $fail failed, $skip skipped"
exit $fail
