#!/usr/bin/env bash
#
# Runs persist round-trip fuzz cases (from gen_persist.py). Each case is a
# self-checking Frame system: transpile, compile, run — case prints PASS on
# success, FAIL on any save/restore mismatch.
#
# Supported targets this version: python_3, javascript. TypeScript would
# work but requires tsx / tsc on PATH.

set -o pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
FRAMEC=${FRAMEC:-/Users/marktruluck/projects/framepiler/target/release/framec}
CASES_DIR=$SCRIPT_DIR/cases_persist
OUT_DIR=$SCRIPT_DIR/out_persist
LOG_DIR=$SCRIPT_DIR/logs_persist
mkdir -p "$OUT_DIR" "$LOG_DIR"

LANGS=${@:-"python_3 javascript"}

summary=$LOG_DIR/summary.tsv
: > "$summary"
printf "lang\tcase\tstage\tresult\terror\n" >> "$summary"

lang_to_ext() {
    case "$1" in
        python_3) echo fpy ;;
        javascript) echo fjs ;;
        typescript) echo fts ;;
    esac
}

run_one() {
    local lang=$1
    local case_file=$2
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
    case "$lang" in
        python_3)
            local result
            result=$(python3 "$gen" 2>&1)
            if echo "$result" | grep -q "^PASS:"; then
                printf "%s\t%s\trun\tPASS\t\n" "$lang" "$case_id" >> "$summary"
            else
                local e=$(echo "$result" | tail -3 | tr '\n' '|' | head -c 220)
                printf "%s\t%s\trun\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
                return 1
            fi
            ;;
        javascript)
            # ESM — rename to .mjs and run under node
            local mjs="${gen%.js}.mjs"
            cp "$gen" "$mjs"
            local result
            result=$(node "$mjs" 2>&1)
            if echo "$result" | grep -q "^PASS:"; then
                printf "%s\t%s\trun\tPASS\t\n" "$lang" "$case_id" >> "$summary"
            else
                local e=$(echo "$result" | tail -3 | tr '\n' '|' | head -c 220)
                printf "%s\t%s\trun\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
                return 1
            fi
            ;;
        *)
            printf "%s\t%s\trun\tSKIP_UNSUPPORTED\t\n" "$lang" "$case_id" >> "$summary"
            ;;
    esac
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
awk -F'\t' 'NR>1 && $4=="FAIL" {print $1"  "$2"  "$3}' "$summary" | head -20
