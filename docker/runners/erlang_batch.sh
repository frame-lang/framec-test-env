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
# Exclude /tests/erlang/multi/ — those are processed by the
# multi-source sweep below as one logical TAP test per directory.
lang_tests=$(find /tests/erlang -name "*.$ext" -not -path '*/multi/*' 2>/dev/null | sort)
if [ -n "$lang_tests" ]; then
    tests="$tests
$lang_tests"
fi

# Multi-source cases: each tests/erlang/multi/<case>/ directory is one
# logical test that contains multiple .ferl files (one @@system each)
# plus a driver.escript. Erlang requires one -module per file, so
# multi-system Frame on Erlang must be split. The dir-as-test layout
# wraps that split into a single matrix entry. Discover the dirs
# here; they are processed after the single-source sweep below.
multi_dirs=$(find /tests/erlang/multi -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)
multi_count=$(echo "$multi_dirs" | grep -c . || echo 0)
single_count=$(echo "$tests" | grep -c . || echo 0)
test_count=$((single_count + multi_count))
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
    # Sidecar driver convention: if `<test>.driver.escript` exists
    # alongside `<test>.ferl`, copy it to `run_test.escript` and skip
    # the generic export-walking driver. Lets a test author assertions
    # (pattern matches, io:format("ok …"), exit-on-mismatch) instead of
    # relying on the smoke-test driver that just calls every export.
    sidecar="${test_file%.ferl}.driver.escript"
    if [ -f "$sidecar" ]; then
        escript_path="$work_dir/run_test.escript"
        cp "$sidecar" "$escript_path"
        chmod +x "$escript_path"
        printf '%s\tRUN\t%s\t%s\n' "$test_num" "$test_name" "$sanitized" >> "$MANIFEST"
        continue
    fi

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

# ---- Multi-source sweep ----
# Each tests/erlang/multi/<case>/ dir is one logical TAP test. The dir
# contains N .ferl sources (one @@system each) plus a driver.escript.
# We transpile each .ferl in turn (renaming the output to match its
# -module() directive), append the resulting .erl set to erlc_jobs.tsv
# as one space-separated target list, and copy the driver.escript to
# work_dir/run_test.escript so the existing parallel-execute step
# picks it up unchanged.
for case_dir in $multi_dirs; do
    test_num=$((test_num + 1))
    case_name=$(basename "$case_dir")

    # Per-case @@skip comment in any .ferl skips the whole dir.
    if grep -q "@@skip\|@skip" "$case_dir"/*.ferl 2>/dev/null; then
        printf '%s\tSKIP\t%s\n' "$test_num" "$case_name" >> "$MANIFEST"
        continue
    fi

    sanitized="t${test_num}_$(printf '%s' "$case_name" | sed 's/[^A-Za-z0-9_]/_/g')"
    work_dir="$WORK_ROOT/${sanitized}"
    mkdir -p "$work_dir"

    transpile_failed=false
    erls=""
    for ferl in "$case_dir"/*.ferl; do
        [ -f "$ferl" ] || continue
        ferl_dir=$(mktemp -d)
        if ! framec_cached "$target" "$ferl_dir" "$ferl" /tmp/compile_err; then
            err_line=$(head -5 /tmp/compile_err 2>/dev/null | tr '\n' '\\' | sed 's/\\$//' | sed 's/\\/\\n/g')
            printf '%s\tTRANSPILE_FAIL\t%s\t\t%s\n' "$test_num" "$case_name" "$err_line" >> "$MANIFEST"
            transpile_failed=true
            break
        fi
        out_erl=$(ls "$ferl_dir"/*.erl 2>/dev/null | head -1)
        if [ -z "$out_erl" ]; then
            printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$case_name" >> "$MANIFEST"
            transpile_failed=true
            break
        fi
        erl_module=$(grep -m1 "^-module(" "$out_erl" | sed 's/-module(\(.*\))\./\1/')
        if [ -z "$erl_module" ]; then
            printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$case_name" >> "$MANIFEST"
            transpile_failed=true
            break
        fi
        target_erl="$work_dir/${erl_module}.erl"
        mv "$out_erl" "$target_erl"
        erls="$erls $target_erl"
    done
    if [ "$transpile_failed" = "true" ]; then
        continue
    fi
    erls=$(echo "$erls" | sed 's/^ //')

    if [ -z "$erls" ]; then
        printf '%s\tNO_OUTPUT\t%s\n' "$test_num" "$case_name" >> "$MANIFEST"
        continue
    fi

    # Driver: the case dir must contain exactly one driver.escript
    # (or <case>.driver.escript). It is copied verbatim into the
    # work dir as run_test.escript so the standard execute step
    # finds it. The driver is responsible for code:add_patha("."),
    # gen_statem:start_link/N, assertions, and io:format("ok 1 - …").
    driver_src="$case_dir/driver.escript"
    if [ ! -f "$driver_src" ]; then
        driver_src="$case_dir/${case_name}.driver.escript"
    fi
    if [ ! -f "$driver_src" ]; then
        printf '%s\tNO_DRIVER\t%s\n' "$test_num" "$case_name" >> "$MANIFEST"
        continue
    fi
    cp "$driver_src" "$work_dir/run_test.escript"
    chmod +x "$work_dir/run_test.escript"

    if [ "$COMPILE_ONLY" = "true" ]; then
        printf '%s\tCOMPILE_ONLY\t%s\n' "$test_num" "$case_name" >> "$MANIFEST"
    fi

    # Multi-source erlc jobs go to a separate file because the
    # third field is a space-separated list — xargs -n 3 (used
    # by the single-source parallel path below) would word-split
    # it. Process this file with a tab-delimited reader instead.
    printf '%s\t%s\t%s\n' "$test_num" "$work_dir" "$erls" >> "$WORK_ROOT/multi_erlc_jobs.tsv"
    printf '%s\tRUN\t%s\t%s\n' "$test_num" "$case_name" "$sanitized" >> "$MANIFEST"
done

# ---- Parallel erlc compile (deferred from per-test loop) ----
# Each test's deferred erlc target was logged to erlc_jobs.tsv. Compile
# them in parallel; failures get marked COMPILE_FAIL by patching the
# MANIFEST after.
if [ -s "$WORK_ROOT/erlc_jobs.tsv" ]; then
    erlc_one() {
        local num="$1"
        local work_dir="$2"
        # Third arg is one path for single-source cases, or a
        # space-separated list of paths for multi-source dirs.
        # Intentionally unquoted so the shell word-splits it.
        local target_erls="$3"
        # shellcheck disable=SC2086
        if erlc -o "$work_dir" $target_erls 2>"$work_dir/erlc_err"; then
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

# ---- Multi-source erlc compile (sequential) ----
# Each row's third field is a space-separated list of .erl paths
# to compile together; tab-delimited read keeps the third field
# intact, then we let `erlc -o "$work_dir" $erls` word-split
# inside the call.
if [ -s "$WORK_ROOT/multi_erlc_jobs.tsv" ]; then
    while IFS=$'\t' read -r num work_dir erls; do
        # shellcheck disable=SC2086
        if erlc -o "$work_dir" $erls 2>"$work_dir/erlc_err"; then
            echo 0 > "$work_dir/erlc_rc"
        else
            echo 1 > "$work_dir/erlc_rc"
            test_name=$(awk -F'\t' -v n="$num" '$1 == n {print $3}' "$MANIFEST")
            tmp=$(mktemp)
            awk -F'\t' -v n="$num" -v name="$test_name" 'BEGIN{OFS="\t"}
                $1 == n { print n, "COMPILE_FAIL", name; next }
                { print }' "$MANIFEST" > "$tmp"
            mv "$tmp" "$MANIFEST"
        fi
    done < "$WORK_ROOT/multi_erlc_jobs.tsv"
fi

if [ "$COMPILE_ONLY" = "true" ]; then
    pass=0; fail=0; skip=0
    while IFS=$'\t' read -r num status name rest; do
        case "$status" in
            SKIP)                   echo "ok $num - $name # SKIP";                              skip=$((skip+1)) ;;
            TRANSPILE_ERROR_OK)     echo "ok $num - $name # correctly rejected by transpiler";  pass=$((pass+1)) ;;
            TRANSPILE_FAIL)         echo "not ok $num - $name # transpile failed";              fail=$((fail+1)) ;;
            NO_OUTPUT)              echo "not ok $num - $name # no output file";                fail=$((fail+1)) ;;
            NO_DRIVER)              echo "not ok $num - $name # multi-source case missing driver.escript"; fail=$((fail+1)) ;;
            COMPILE_FAIL)           echo "not ok $num - $name # erlc failed";                   fail=$((fail+1)) ;;
            COMPILE_ONLY|RUN)       echo "ok $num - $name # transpiled";                        pass=$((pass+1)) ;;
        esac
    done < "$MANIFEST"
    echo ""
    echo "# erlang: $pass passed, $fail failed, $skip skipped"
    exit $fail
fi

# ---- Batched parallel BEAM execution ----
#
# Each escript boots its own BEAM (~250-500ms cold). We collapse N
# escripts into one BEAM by:
#   1. Converting each `run_test.escript` into a callable module
#      `test_<sanitized>.erl` exporting `run/0` (drop the
#      `init:stop()` / `halt(_)` and the escript shebang).
#   2. Compiling all converted modules + their system modules
#      into a per-batch shared dir.
#   3. Running ONE `erl -noshell` invocation per batch that adds
#      each test's dir to the code path, calls `Mod:run()` with a
#      try/catch wrapper, prints `==FRAME-TEST-BEGIN/END==` markers
#      so the classifier can slice per-test stdout.
#   4. Running B batches in parallel via xargs -P.
TIMEOUT_SEC="${ERLANG_TEST_TIMEOUT:-120}"
BATCH_SIZE="${ERLANG_BATCH_SIZE:-50}"
export STATUS_DIR WORK_ROOT TIMEOUT_SEC BATCH_SIZE

# Convert each RUN-row escript into a callable module. Keep the
# original escript for tests that use sidecar drivers with patterns
# we can't safely transform (multi-line `main(_) -> ... main_helper(...)`,
# helper functions, etc.). Heuristic: only convert escripts that
# match the simple `main(_) -> body, init:stop().` shape that the
# generated path always emits.
convert_to_module() {
    local sanitized="$1"
    local dir="$WORK_ROOT/$sanitized"
    local escript="$dir/run_test.escript"
    [ -f "$escript" ] || return 1
    local mod_name="test_${sanitized}"
    local mod_file="$dir/${mod_name}.erl"
    # Strip shebang, replace `main(_) ->` with `run() ->`, drop
    # trailing `init:stop().` / `halt(_).` calls. Any helper
    # functions defined after main/1 are kept as-is (they get
    # exported below).
    # Replace `init:stop().` / `halt(...).` with `ok.` (the final
    # expression must terminate with `.` and the previous chain of
    # statements ends with `,`, so we can't just delete the line).
    awk -v MOD="$mod_name" '
        BEGIN { print "-module(" MOD ")." ; print "-compile(export_all)." }
        /^#!/ { next }
        /^main *\( *_? *\) *->/ {
            sub(/^main *\( *_? *\) *->/, "run() ->")
            print
            next
        }
        /^[[:space:]]*init:stop\(\)\./ { print "    ok."; next }
        /^[[:space:]]*halt\([^)]*\)\./ { print "    ok."; next }
        /^[[:space:]]*halt\(\)\./ { print "    ok."; next }
        { print }
    ' "$escript" > "$mod_file"
    # erlc writes errors to stdout, not stderr; capture both.
    if ! erlc -o "$dir" "$mod_file" >"$dir/test_mod_erlc_err" 2>&1; then
        rm -f "$mod_file" "$dir/${mod_name}.beam"
        return 1
    fi
    return 0
}
export -f convert_to_module

awk -F'\t' '$2 == "RUN" { print $4 }' "$MANIFEST" | \
    xargs -n 1 -P "$JOBS" -I{} bash -c 'convert_to_module "$@" || true' _ {}

# Build the batch runner module. Compile once into a shared dir.
export BATCH_RUNNER_DIR="$WORK_ROOT/batch_runner"
mkdir -p "$BATCH_RUNNER_DIR"
cat > "$BATCH_RUNNER_DIR/batch_runner.erl" <<'ERLEOF'
-module(batch_runner).
-export([main/1]).

%% Args alternating: <module_name> <work_dir> ...
main(Args) ->
    run_pairs(Args),
    init:stop().

%% Load every .beam in Dir (force-replacing any previously-loaded
%% module with the same name). Tests can share short module names
%% like `s` across fixtures, so we can't trust the codeserver's
%% in-memory copy of a module to be the right one for this test.
load_dir_modules(Dir) ->
    case file:list_dir(Dir) of
        {ok, Names} ->
            lists:foreach(fun(F) ->
                case lists:suffix(".beam", F) of
                    true ->
                        Mod = list_to_atom(filename:rootname(F)),
                        code:purge(Mod),
                        code:delete(Mod),
                        Path = filename:join(Dir, filename:rootname(F)),
                        code:load_abs(Path);
                    false -> ok
                end
            end, Names);
        _ -> ok
    end.

%% Purge every module loaded from Dir so the next test gets a
%% clean slate. We can't tell from the codeserver which module
%% came from which dir, so we just purge anything matching a
%% .beam file in this Dir.
purge_dir_modules(Dir) ->
    case file:list_dir(Dir) of
        {ok, Names} ->
            lists:foreach(fun(F) ->
                case lists:suffix(".beam", F) of
                    true ->
                        Mod = list_to_atom(filename:rootname(F)),
                        code:purge(Mod),
                        code:delete(Mod);
                    false -> ok
                end
            end, Names);
        _ -> ok
    end.

run_pairs([]) -> ok;
run_pairs([Mod, Dir | Rest]) ->
    ModAtom = list_to_atom(Mod),
    io:format("==FRAME-TEST-BEGIN== ~s~n", [Mod]),
    %% Force-load every .beam in this test's dir so module names
    %% shared across tests resolve to THIS test's compile.
    load_dir_modules(Dir),
    try
        ModAtom:run()
    catch
        C:E:S ->
            io:format("ERLANG-BATCH-EXC ~p:~p~nstack: ~p~n", [C, E, S])
    end,
    io:format("==FRAME-TEST-END== ~s~n", [Mod]),
    purge_dir_modules(Dir),
    run_pairs(Rest).
ERLEOF
if ! erlc -o "$BATCH_RUNNER_DIR" "$BATCH_RUNNER_DIR/batch_runner.erl"; then
    echo "FATAL: batch_runner failed to compile" >&2
    exit 1
fi

# Build batch manifests. Each entry: <test_module_name>\t<work_dir>
# Tests whose convert_to_module failed (no test_<sanitized>.beam)
# fall back to the legacy per-test escript run.
BATCH_DIR="$STATUS_DIR/batches"
LEGACY_LIST="$STATUS_DIR/legacy.tsv"
mkdir -p "$BATCH_DIR"
: > "$LEGACY_LIST"
batch_idx=0
row_idx=0
batch_file="$BATCH_DIR/batch_$(printf '%04d' $batch_idx).tsv"
: > "$batch_file"

awk -F'\t' '$2 == "RUN" { print $4 }' "$MANIFEST" | while read -r sanitized; do
    dir="$WORK_ROOT/$sanitized"
    mod_name="test_${sanitized}"
    if [ -f "$dir/${mod_name}.beam" ]; then
        printf '%s\t%s\n' "$mod_name" "$dir" >> "$batch_file"
        row_idx=$((row_idx + 1))
        if [ "$row_idx" -ge "$BATCH_SIZE" ]; then
            batch_idx=$((batch_idx + 1))
            row_idx=0
            batch_file="$BATCH_DIR/batch_$(printf '%04d' $batch_idx).tsv"
            : > "$batch_file"
        fi
    else
        printf '%s\n' "$sanitized" >> "$LEGACY_LIST"
    fi
done
[ ! -s "$batch_file" ] && rm -f "$batch_file"

run_batch() {
    local batch_id="$1"
    local manifest="$2"
    local batch_out="$STATUS_DIR/batch_${batch_id}.out"

    # Build args list: alternating module names and work dirs.
    local -a args
    while IFS=$'\t' read -r mod dir; do
        args+=("$mod" "$dir")
    done < "$manifest"
    [ "${#args[@]}" -eq 0 ] && return

    # Use `erl -run Mod main Args...` form: each token after `-run`
    # becomes an arg. Module is loaded from -pa code path.
    setsid --wait timeout "$TIMEOUT_SEC" erl -noshell \
        -pa "$BATCH_RUNNER_DIR" \
        -run batch_runner main "${args[@]}" \
        > "$batch_out" 2>&1
    local rc=$?
    sync "$batch_out" 2>/dev/null || true

    awk -v OUTDIR="$STATUS_DIR" -v RC="$rc" '
        /^==FRAME-TEST-BEGIN== / {
            mod = $2
            sanitized = mod
            sub(/^test_/, "", sanitized)
            cur = OUTDIR "/" sanitized ".out"
            cur_rc = OUTDIR "/" sanitized ".rc"
            saw_begin = 1
            content = ""
            saw_exc = 0
            next
        }
        /^==FRAME-TEST-END== / {
            if (saw_begin) {
                printf "%s", content > cur
                close(cur)
                if (RC == 124) { print "124" > cur_rc }
                else if (saw_exc) { print "1" > cur_rc }
                else { print "0" > cur_rc }
                close(cur_rc)
                saw_begin = 0
            }
            next
        }
        /^ERLANG-BATCH-EXC / { saw_exc = 1 }
        saw_begin { content = content $0 "\n" }
    ' "$batch_out"
}
export -f run_batch

# Run batches in parallel.
ls "$BATCH_DIR"/batch_*.tsv 2>/dev/null | \
    xargs -n 1 -P "$JOBS" -I{} bash -c '
        f="$1"
        id=$(basename "$f" .tsv | sed "s/batch_//")
        run_batch "$id" "$f"
    ' _ {}

# Legacy fallback: run any test that didn't convert via the
# original per-test escript path.
run_legacy() {
    local sanitized="$1"
    local dir="$WORK_ROOT/$sanitized"
    ( cd "$dir" && timeout "$TIMEOUT_SEC" escript run_test.escript ) \
        > "$STATUS_DIR/${sanitized}.out" 2>&1
    echo $? > "$STATUS_DIR/${sanitized}.rc"
}
export -f run_legacy

if [ -s "$LEGACY_LIST" ]; then
    cat "$LEGACY_LIST" | xargs -n 1 -P "$JOBS" -I{} bash -c 'run_legacy "$@"' _ {}
fi

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
        NO_DRIVER)
            echo "not ok $num - $name # multi-source case missing driver.escript"; fail=$((fail+1)) ;;
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
