#!/bin/bash
# Batched Erlang test runner. Each Erlang test needs a per-test escript
# driver (the generator is copied from runner.sh). We keep that logic but
# execute all escripts in parallel — escript cold start (~500ms per VM)
# is the dominant per-test cost; xargs -P cuts wall time proportionally
# with available cores.

set -uo pipefail

# Source-hash cache for framec: skips re-transpile when source
# + framec version haven't changed since last run.
. /framec_cached.sh

OUTPUT="/output"
WORK_ROOT="/tmp/erlang_out"
MANIFEST="/tmp/erlang_manifest.tsv"
STATUS_DIR="/tmp/erlang_status"
COMPILE_ONLY="${COMPILE_ONLY:-false}"
JOBS="${ERLANG_TEST_JOBS:-$(nproc 2>/dev/null || echo 4)}"

target="erlang"
ext="ferl"
out_ext="erl"

mkdir -p "$OUTPUT"
rm -rf "$WORK_ROOT" "$MANIFEST" "$STATUS_DIR" 2>/dev/null
mkdir -p "$WORK_ROOT" "$STATUS_DIR"
: > "$MANIFEST"

tests=$(find /tests/common/positive -name "*.$ext" 2>/dev/null | sort)
lang_tests=$(find /tests/erlang -name "*.$ext" 2>/dev/null | sort)
if [ -n "$lang_tests" ]; then
    tests="$tests
$lang_tests"
fi

test_count=$(echo "$tests" | grep -c . || echo 0)
if [ "$test_count" -eq 0 ]; then
    echo "TAP version 14"
    echo "1..0 # SKIP no erlang tests found"
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
    work_dir="$WORK_ROOT/${sanitized}"
    mkdir -p "$work_dir"

    if ! framec_cached "$target" "$work_dir" "$test_file" /tmp/compile_err; then
        if echo "$test_file" | grep -q "transpile-error"; then
            printf '%s\tTRANSPILE_ERROR_OK\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        else
            err_line=$(head -5 /tmp/compile_err 2>/dev/null | tr '\n' '\\' | sed 's/\\$//' | sed 's/\\/\\n/g')
            printf '%s\tTRANSPILE_FAIL\t%s\t\t%s\n' "$test_num" "$test_name" "$err_line" >> "$MANIFEST"
        fi
        continue
    fi

    out_file=$(ls "$work_dir"/*.erl 2>/dev/null | head -1)
    if [ -z "$out_file" ]; then
        printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    if [ "$COMPILE_ONLY" = "true" ]; then
        printf '%s\tCOMPILE_ONLY\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi

    # Rename file to match the -module() directive so erlc is happy.
    erl_module=$(grep -m1 "^-module(" "$out_file" | sed 's/-module(\(.*\))\./\1/')
    if [ -z "$erl_module" ]; then
        printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$test_name" >> "$MANIFEST"
        continue
    fi
    target_erl="$work_dir/${erl_module}.erl"
    if [ "$out_file" != "$target_erl" ]; then
        mv "$out_file" "$target_erl"
    fi

    # Defer erlc — collect targets here, compile in parallel after the
    # loop. erlc cold start (~500 ms × 217 tests) was the dominant
    # serial cost; xargs -P drops it to ~total/cores.
    printf '%s\t%s\t%s\n' "$test_num" "$work_dir" "$target_erl" >> "$WORK_ROOT/erlc_jobs.tsv"

    # ---- escript generation (logic preserved from runner.sh) ----
    start_link_arity=$(grep "^-export" "$target_erl" | head -1 | grep -oE 'start_link/[0-9]+' | sed 's|start_link/||')
    start_link_arity=${start_link_arity:-0}

    start_link_args=""
    if [ "$start_link_arity" -gt 0 ]; then
        sys_line=$(grep -m1 "^@@system " "$test_file" 2>/dev/null)
        sys_params_str=$(echo "$sys_line" | sed -n 's/.*@@system [A-Za-z_][A-Za-z0-9_]*[[:space:]]*(\(.*\))[[:space:]]*{.*/\1/p')
        if [ -n "$sys_params_str" ]; then
            echo "$sys_params_str" | tr ',' '\n' | while read -r p; do
                echo "$p" | sed -n 's/.*: *\([a-zA-Z][a-zA-Z0-9_]*\).*/\1/p'
            done > "$work_dir/sys_param_types.txt"
        fi
        for i in $(seq 1 "$start_link_arity"); do
            ptype=""
            if [ -f "$work_dir/sys_param_types.txt" ]; then
                ptype=$(sed -n "${i}p" "$work_dir/sys_param_types.txt")
            fi
            case "$ptype" in
                bool|boolean)           val="false" ;;
                str|string|String)      val="\"\"" ;;
                int|float|number|Int|Float) val="0" ;;
                *)                      val="undefined" ;;
            esac
            if [ -z "$start_link_args" ]; then
                start_link_args="$val"
            else
                start_link_args="$start_link_args, $val"
            fi
        done
    fi

    erl_exports=$(grep "^-export" "$target_erl" | head -1 | sed 's/-export(\[//;s/\])\.//' | sed -E 's/start_link\/[0-9]+,?//' | sed 's/,\s*$//' | tr ',' '\n' | grep -v '^$' | sed 's|/| |')

    escript_path="$work_dir/run_test.escript"
    cat > "$escript_path" << ESCRIPT
#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    {ok, Pid} = ${erl_module}:start_link(${start_link_args}),
ESCRIPT
    while IFS=' ' read -r fname arity; do
        fname=$(echo "$fname" | tr -d ' ')
        arity=$(echo "$arity" | tr -d ' ')
        if [ -z "$fname" ] || [ "$fname" = "start_link" ]; then continue; fi
        args="Pid"
        remaining=$((arity - 1))
        if [ "$remaining" -gt 0 ]; then
            iface_line=$(grep "${fname}(" "$test_file" 2>/dev/null | head -1)
            types=""
            if [ -n "$iface_line" ]; then
                params_str=$(echo "$iface_line" | sed "s/.*${fname}(//;s/).*//")
                types=$(echo "$params_str" | tr ',' '\n' | while read -r p; do
                    echo "$p" | sed -n 's/.*: *\([a-zA-Z]*\).*/\1/p'
                done)
            fi
            idx=0
            for i in $(seq 1 "$remaining"); do
                idx=$((idx + 1))
                ptype=$(echo "$types" | sed -n "${idx}p")
                case "$ptype" in
                    bool|boolean)      args="$args, false" ;;
                    str|string|String) args="$args, \"\"" ;;
                    *)                 args="$args, 0" ;;
                esac
            done
        fi
        echo "    _ = ${erl_module}:${fname}(${args})," >> "$escript_path"
    done <<< "$erl_exports"
    cat >> "$escript_path" << ESCRIPT
    io:format("ok 1 - ${test_name}~n"),
    init:stop().
ESCRIPT
    chmod +x "$escript_path"

    printf '%s\tRUN\t%s\t%s\n' "$test_num" "$test_name" "$sanitized" >> "$MANIFEST"
done

# ---- Parallel erlc compile (deferred from per-test loop) ----
# Each test's deferred erlc target was logged to erlc_jobs.tsv. Compile
# them in parallel; failures get marked COMPILE_FAIL by patching the
# MANIFEST after.
if [ -s "$WORK_ROOT/erlc_jobs.tsv" ]; then
    erlc_one() {
        local num="$1"
        local work_dir="$2"
        local target_erl="$3"
        if erlc -o "$work_dir" "$target_erl" 2>"$work_dir/erlc_err"; then
            echo 0 > "$work_dir/erlc_rc"
        else
            echo 1 > "$work_dir/erlc_rc"
        fi
    }
    export -f erlc_one
    awk -F'\t' '{print $1; print $2; print $3}' "$WORK_ROOT/erlc_jobs.tsv" | \
        xargs -n 3 -P "$JOBS" bash -c 'erlc_one "$@"' _

    # Mark COMPILE_FAIL for any test whose erlc returned non-zero.
    while IFS=$'\t' read -r num work_dir target_erl; do
        if [ "$(cat "$work_dir/erlc_rc" 2>/dev/null)" != "0" ]; then
            test_name=$(awk -F'\t' -v n="$num" '$1 == n {print $3}' "$MANIFEST")
            # Replace the RUN row with COMPILE_FAIL.
            tmp=$(mktemp)
            awk -F'\t' -v n="$num" -v name="$test_name" 'BEGIN{OFS="\t"}
                $1 == n { print n, "COMPILE_FAIL", name; next }
                { print }' "$MANIFEST" > "$tmp"
            mv "$tmp" "$MANIFEST"
        fi
    done < "$WORK_ROOT/erlc_jobs.tsv"
fi

if [ "$COMPILE_ONLY" = "true" ]; then
    pass=0; fail=0; skip=0
    while IFS=$'\t' read -r num status name rest; do
        case "$status" in
            SKIP)                   echo "ok $num - $name # SKIP";                              skip=$((skip+1)) ;;
            TRANSPILE_ERROR_OK)     echo "ok $num - $name # correctly rejected by transpiler";  pass=$((pass+1)) ;;
            TRANSPILE_FAIL)         echo "not ok $num - $name # transpile failed";              fail=$((fail+1)) ;;
            NO_OUTPUT)              echo "not ok $num - $name # no output file";                fail=$((fail+1)) ;;
            COMPILE_FAIL)           echo "not ok $num - $name # erlc failed";                   fail=$((fail+1)) ;;
            COMPILE_ONLY|RUN)       echo "ok $num - $name # transpiled";                        pass=$((pass+1)) ;;
        esac
    done < "$MANIFEST"
    echo ""
    echo "# erlang: $pass passed, $fail failed, $skip skipped"
    exit $fail
fi

# ---- Parallel escript execution ----
TIMEOUT_SEC="${ERLANG_TEST_TIMEOUT:-30}"
export STATUS_DIR WORK_ROOT TIMEOUT_SEC

run_one() {
    local sanitized="$1"
    local dir="$WORK_ROOT/$sanitized"
    # File redirect rather than bash subshell capture: preserves NUL
    # bytes, multibyte boundaries, and arbitrary binary output.
    ( cd "$dir" && timeout "$TIMEOUT_SEC" escript run_test.escript ) \
        > "$STATUS_DIR/${sanitized}.out" 2>&1
    echo $? > "$STATUS_DIR/${sanitized}.rc"
}
export -f run_one

awk -F'\t' '$2 == "RUN" { print $4 }' "$MANIFEST" | \
    xargs -n 1 -P "$JOBS" -I{} bash -c 'run_one "$@"' _ {}

# ---- Collect + emit TAP ----
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
        COMPILE_FAIL)
            echo "not ok $num - $name # erlc failed"; fail=$((fail+1)) ;;
        RUN)
            rc_file="$STATUS_DIR/${sanitized}.rc"
            out_file="$STATUS_DIR/${sanitized}.out"
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
                echo "not ok $num - $name # unrecognized output"
                echo "$out" | head -3 | sed 's/^/  # /'
                fail=$((fail+1))
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
echo "# erlang: $pass passed, $fail failed, $skip skipped"
exit $fail
