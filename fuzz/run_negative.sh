#!/usr/bin/env bash
#
# Phase 8 negative-case runner. Uses the same `transpile_case` classifier
# as run.sh: each case file declares `# @@expect-error: E<NNN>` and is
# expected to be REJECTED by framec with that exact error code.
#
# Cases live in `cases_negative/<name>.fpy`. They're intentionally
# small Frame sources (10–20 lines) that trigger one specific framec
# validator error each. Adding a case = author the .fpy + verify the
# directive matches the actual emitted error.
#
# Usage:
#   ./run_negative.sh                 # all cases via python_3 target
#   ./run_negative.sh -l java         # all cases via java target
#
# The classifier itself ignores the target language — it just checks
# whether framec's stderr contains the expected error code. Picking
# python_3 by default is fine for E113/E60x which fire for any target.

set -o pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
FRAMEC=${FRAMEC:-$(cd "$SCRIPT_DIR/../../framepiler" 2>/dev/null && pwd)/target/release/framec}
if [ ! -x "$FRAMEC" ]; then
    FRAMEC=/Users/marktruluck/projects/framepiler/target/release/framec
fi

LANG=python_3
while [ $# -gt 0 ]; do
    case "$1" in
        -l|--lang) LANG=$2; shift 2 ;;
        -h|--help)
            echo "Usage: $0 [-l <lang>]"
            exit 0
            ;;
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
done

CASES_DIR=$SCRIPT_DIR/cases_negative
OUT_DIR=$SCRIPT_DIR/out_negative
LOG_DIR=$SCRIPT_DIR/logs_negative
mkdir -p "$OUT_DIR" "$LOG_DIR"

if [ ! -d "$CASES_DIR" ] || ! ls "$CASES_DIR"/*.fpy >/dev/null 2>&1; then
    echo "no cases under $CASES_DIR" >&2
    exit 0
fi

summary_file=$LOG_DIR/summary.tsv
: > "$summary_file"
printf "lang\tcase\tstage\tresult\terror\n" >> "$summary_file"

read_expected_error() {
    local case_file=$1
    head -10 "$case_file" 2>/dev/null \
        | grep -m1 -oE '@@expect-error:[[:space:]]*E[0-9]+' \
        | sed 's/.*expect-error:[[:space:]]*//'
}

pass=0; fail=0
for case_file in "$CASES_DIR"/*.fpy; do
    case_id=$(basename "$case_file" .fpy)
    out=$OUT_DIR/$LANG/$case_id
    rm -rf "$out" 2>/dev/null
    mkdir -p "$out"
    errlog=$LOG_DIR/$LANG-$case_id.err

    expected=$(read_expected_error "$case_file")
    if [ -z "$expected" ]; then
        printf "%s\t%s\ttranspile\tFAIL\tno @@expect-error directive\n" \
            "$LANG" "$case_id" >> "$summary_file"
        fail=$((fail+1))
        echo "  FAIL  $case_id  (no @@expect-error directive)"
        continue
    fi

    if "$FRAMEC" compile -l "$LANG" -o "$out" "$case_file" > "$errlog" 2>&1; then
        printf "%s\t%s\ttranspile\tFAIL\texpected %s but transpile succeeded\n" \
            "$LANG" "$case_id" "$expected" >> "$summary_file"
        fail=$((fail+1))
        echo "  FAIL  $case_id  (expected $expected but transpile succeeded)"
        continue
    fi

    if grep -qE "\b${expected}\b" "$errlog"; then
        printf "%s\t%s\ttranspile\tPASS\texpected %s\n" \
            "$LANG" "$case_id" "$expected" >> "$summary_file"
        pass=$((pass+1))
        echo "  ok    $case_id  ($expected)"
    else
        actual=$(grep -oE 'E[0-9]+' "$errlog" | head -1)
        printf "%s\t%s\ttranspile\tFAIL\texpected %s, got %s\n" \
            "$LANG" "$case_id" "$expected" "$actual" >> "$summary_file"
        fail=$((fail+1))
        echo "  FAIL  $case_id  (expected $expected, got ${actual:-no error code})"
    fi
done

echo ""
echo "$LANG: $pass pass / $fail fail"
[ $fail -eq 0 ]
