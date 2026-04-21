#!/usr/bin/env bash
# Runs @@:self-call fuzz cases. Each case is self-checking.

set -o pipefail
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
FRAMEC=${FRAMEC:-/Users/marktruluck/projects/framepiler/target/release/framec}
CASES_DIR=$SCRIPT_DIR/cases_selfcall
OUT_DIR=$SCRIPT_DIR/out_selfcall
LOG_DIR=$SCRIPT_DIR/logs_selfcall
mkdir -p "$OUT_DIR" "$LOG_DIR"
LANGS=${@:-"python_3 javascript erlang"}
summary=$LOG_DIR/summary.tsv
: > "$summary"
printf "lang\tcase\tstage\tresult\terror\n" >> "$summary"

lang_to_ext() {
    case "$1" in
        python_3) echo fpy ;;
        javascript) echo fjs ;;
        erlang) echo ferl ;;
    esac
}

run_one() {
    local lang=$1 case_file=$2
    local case_id=$(basename "$case_file" | sed 's/\.f[a-z]*$//')
    local out="$OUT_DIR/$lang/$case_id"
    local errlog="$LOG_DIR/$lang-$case_id.err"
    rm -rf "$out" 2>/dev/null
    mkdir -p "$out"
    if ! "$FRAMEC" compile -l "$lang" -o "$out" "$case_file" > "$errlog" 2>&1; then
        local e=$(head -3 "$errlog" | grep -v frame_runtime | tr '\n' '|' | head -c 220)
        printf "%s\t%s\ttranspile\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
        return 1
    fi
    local gen=$(ls "$out"/*.* 2>/dev/null | head -1)
    local result=""
    case "$lang" in
        python_3)
            result=$(python3 "$gen" 2>&1)
            ;;
        javascript)
            local mjs="${gen%.js}.mjs"
            cp "$gen" "$mjs"
            result=$(node "$mjs" 2>&1)
            ;;
        erlang)
            # Expected values are stashed as comments in the source file
            # by the generator (% FUZZ_EXPECTED_STATE / _TRACE). Parse those.
            local src=$(dirname "$case_file")/$(basename "$case_file")
            local expected_state=$(grep '^% FUZZ_EXPECTED_STATE:' "$case_file" | awk '{print $3}')
            local expected_trace=$(grep '^% FUZZ_EXPECTED_TRACE:' "$case_file" | awk '{print $3}')
            # Rename to module name so erlc accepts it
            local mod=$(grep -m1 '^-module(' "$gen" | sed 's/-module(\(.*\))\./\1/')
            if [ -z "$mod" ]; then
                printf "%s\t%s\tcompile\tFAIL\tno -module\n" "$lang" "$case_id" >> "$summary"
                return 1
            fi
            local target_erl="$out/${mod}.erl"
            cp "$gen" "$target_erl"
            if ! (cd "$out" && erlc "$target_erl") 2>"$errlog"; then
                local e=$(head -3 "$errlog" | tr '\n' '|' | head -c 220)
                printf "%s\t%s\tcompile\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
                return 1
            fi
            # Build escript driver
            local escript="$out/drive.escript"
            cat > "$escript" << ESCRIPT
#!/usr/bin/env escript
main(_) ->
    code:add_patha("$out"),
    {ok, Pid} = ${mod}:start_link(),
    ${mod}:drive(Pid),
    State = ${mod}:status(Pid),
    Trace = ${mod}:trace(Pid),
    ExpectedState = "$expected_state",
    ExpectedTrace = $expected_trace,
    case {State, Trace} of
        {ExpectedState, ExpectedTrace} ->
            io:format("PASS: self-call guard~n");
        {Other, _} when Other =/= ExpectedState ->
            io:format("FAIL: state ~p != ~p~n", [Other, ExpectedState]),
            halt(1);
        _ ->
            io:format("FAIL: trace ~p != ~p~n", [Trace, ExpectedTrace]),
            halt(1)
    end.
ESCRIPT
            result=$(escript "$escript" 2>&1)
            ;;
    esac
    if echo "$result" | grep -q "^PASS:"; then
        printf "%s\t%s\trun\tPASS\t\n" "$lang" "$case_id" >> "$summary"
    else
        local e=$(echo "$result" | tail -4 | tr '\n' '|' | head -c 220)
        printf "%s\t%s\trun\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
        return 1
    fi
}

for lang in $LANGS; do
    ext=$(lang_to_ext "$lang")
    [ -z "$ext" ] && continue
    cases=$(ls "$CASES_DIR/$lang"/case_*.$ext 2>/dev/null | sort)
    total=$(echo "$cases" | grep -c . || echo 0)
    [ "$total" -eq 0 ] && { echo "$lang: no cases"; continue; }
    echo "=== $lang ($total cases) ==="
    for case_file in $cases; do
        run_one "$lang" "$case_file" >/dev/null
    done
    pass=$(awk -v L="$lang" -F'\t' '$1==L && $4=="PASS"{n++} END{print n+0}' "$summary")
    fail=$(awk -v L="$lang" -F'\t' '$1==L && $4=="FAIL"{n++} END{print n+0}' "$summary")
    echo "$lang: $pass pass / $fail fail"
done

echo ""
echo "=== Fails ==="
awk -F'\t' 'NR>1 && $4=="FAIL"' "$summary" | head -5
