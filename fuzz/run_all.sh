#!/usr/bin/env bash
# Phase 0 unified meta-runner — iterates the configured fuzz phases
# applying the standard runner contract (--tier=smoke|core|full,
# --tag=<comma-list>, --lang=<name>) to each.
#
# This is the skeleton (v1). Tier filtering across all phases works
# today by passthrough; tag filtering requires per-phase migration
# to the sidecar-index model (see TEST_INFRA_ROADMAP.md).
#
# Usage:
#   run_all.sh                                        # default --tier=full --lang=all
#   run_all.sh --tier=smoke                           # ~2 min target
#   run_all.sh --tier=full --lang=python_3            # one-lang full
#   run_all.sh --tier=smoke --phases=9,10             # subset
#   run_all.sh --tag=hsm                              # tag-filtered (post-migration)
#
# Phase index:
#   2  persist          (run_fuzz.py --cases ../cases/persist)
#   3  selfcall         (run_fuzz.py --cases ../cases/selfcall)
#   4  hsm-parents      (run_fuzz.py --cases ../cases/hsm)
#   5  operations       (run_fuzz.py --cases ../cases/operations)
#   6  async            (run_fuzz.py --cases ../cases/async)
#   7  multisys         (run_fuzz.py --cases ../cases/multisys)
#   8  negative         (run_negative.sh)
#   9  nested-syntax    (run_nested.sh)
#  10  expression       (run_perm.sh)
#  11  stmt-pair        (run_stmt_pair.sh)
#  12  ctrl-flow        (run_ctrl_flow.sh)
#  13  shadow           (run_shadow.sh)
#  14  hsm-cross        (run_hsm_cross.sh)
#  15  state-args       (run_state_args.sh)
#  16  comments         (run_comments.sh)
#  17  multievent       (run_multievent.sh)
#  19  pushpop          (run_pushpop.sh)
#  20  const-sys        (run_const_sys.sh)
#
# Exit code: 0 if all phases pass, nonzero if any phase failed.

set -o pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
DIFF_HARNESS="$SCRIPT_DIR/diff_harness/run_fuzz.py"

TIER="full"
LANG=""
TAG=""
PHASES_REQUESTED=""

while [ $# -gt 0 ]; do
    case "$1" in
        --tier=*) TIER="${1#--tier=}" ;;
        --tier) shift; TIER="$1" ;;
        --lang=*) LANG="${1#--lang=}" ;;
        --lang) shift; LANG="$1" ;;
        --tag=*) TAG="${1#--tag=}" ;;
        --tag) shift; TAG="$1" ;;
        --phases=*) PHASES_REQUESTED="${1#--phases=}" ;;
        --phases) shift; PHASES_REQUESTED="$1" ;;
        --help|-h)
            echo "Usage: $0 [--tier=smoke|core|full] [--lang=<name>] [--tag=<comma-list>] [--phases=<comma-list>]"
            echo ""
            echo "Phases: 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 19 20 (default: all)"
            echo "Tiers:  smoke (curated, fast), core (phase essentials), full (complete corpus)"
            exit 0
            ;;
        *) echo "unknown arg: $1" >&2; exit 2 ;;
    esac
    shift || true
done

if [ "$TIER" != "smoke" ] && [ "$TIER" != "core" ] && [ "$TIER" != "full" ]; then
    echo "unknown --tier=$TIER (expected smoke|core|full)" >&2
    exit 2
fi

# Default phase list. Phase 1 is infrastructure-only (no runnable
# fuzz). Phases 11+ are not yet built.
ALL_PHASES="2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 19 20"
PHASES=${PHASES_REQUESTED:-$ALL_PHASES}
PHASES=$(echo "$PHASES" | tr ',' ' ')

# Lang-arg propagation: each runner has its own convention. Build a
# pass-through string per backend.
LANG_ARG_NESTED=""
LANG_ARG_PERM=""
LANG_ARG_STMT_PAIR=""
LANG_ARG_CTRL_FLOW=""
LANG_ARG_SHADOW=""
LANG_ARG_HSM_CROSS=""
LANG_ARG_STATE_ARGS=""
LANG_ARG_COMMENTS=""
LANG_ARG_MULTIEVENT=""
LANG_ARG_PUSHPOP=""
LANG_ARG_CONST_SYS=""
LANG_ARG_DIFF=""
LANG_ARG_NEGATIVE=""
if [ -n "$LANG" ]; then
    LANG_ARG_NESTED="$LANG"                    # run_nested.sh takes positional
    LANG_ARG_PERM="--lang=$LANG"               # run_perm.sh
    LANG_ARG_STMT_PAIR="--lang=$LANG"          # run_stmt_pair.sh
    LANG_ARG_CTRL_FLOW="--lang=$LANG"          # run_ctrl_flow.sh
    LANG_ARG_SHADOW="--lang=$LANG"             # run_shadow.sh
    LANG_ARG_HSM_CROSS="--lang=$LANG"          # run_hsm_cross.sh
    LANG_ARG_STATE_ARGS="--lang=$LANG"         # run_state_args.sh
    LANG_ARG_COMMENTS="--lang=$LANG"           # run_comments.sh
    LANG_ARG_MULTIEVENT="--lang=$LANG"         # run_multievent.sh
    LANG_ARG_PUSHPOP="--lang=$LANG"            # run_pushpop.sh
    LANG_ARG_CONST_SYS="--lang=$LANG"          # run_const_sys.sh
    LANG_ARG_DIFF="--langs=$LANG"              # run_fuzz.py
    LANG_ARG_NEGATIVE="-l $LANG"               # run_negative.sh
fi

# Tag-arg propagation. Today: only run_fuzz.py and run_perm.sh
# support tag filtering; others ignore (full corpus).
TAG_ARG_DIFF=""
TAG_ARG_PERM=""
if [ -n "$TAG" ]; then
    TAG_ARG_DIFF="--tag=$TAG"
    # run_perm.sh doesn't yet support --tag — todo as part of Phase 0.
fi

run_phase() {
    local phase=$1
    echo ""
    echo "============================================================"
    echo "Phase $phase ($(phase_name "$phase")) — tier=$TIER"
    echo "============================================================"
    case "$phase" in
        2)  run_diff_harness "persist" ;;
        3)  run_diff_harness "selfcall" ;;
        4)  run_diff_harness "hsm" ;;
        5)  run_diff_harness "operations" ;;
        6)  run_diff_harness "async" ;;
        7)  run_diff_harness "multisys" ;;
        8)  run_negative ;;
        9)  run_nested ;;
        10) run_perm ;;
        11) run_stmt_pair ;;
        12) run_ctrl_flow ;;
        13) run_shadow ;;
        14) run_hsm_cross ;;
        15) run_state_args ;;
        16) run_comments ;;
        17) run_multievent ;;
        19) run_pushpop ;;
        20) run_const_sys ;;
        *)  echo "Phase $phase: unknown" >&2; return 1 ;;
    esac
}

phase_name() {
    case "$1" in
        2) echo "persist" ;;
        3) echo "selfcall" ;;
        4) echo "hsm-parents" ;;
        5) echo "operations" ;;
        6) echo "async" ;;
        7) echo "multisys" ;;
        8) echo "negative" ;;
        9) echo "nested-syntax" ;;
        10) echo "expression" ;;
        11) echo "stmt-pair" ;;
        12) echo "ctrl-flow" ;;
        13) echo "shadow" ;;
        14) echo "hsm-cross" ;;
        15) echo "state-args" ;;
        16) echo "comments" ;;
        17) echo "multievent" ;;
        19) echo "pushpop" ;;
        20) echo "const-sys" ;;
        *) echo "?" ;;
    esac
}

run_diff_harness() {
    local kind=$1
    local cases_dir="$SCRIPT_DIR/cases/$kind"
    if [ ! -d "$cases_dir" ]; then
        echo "  cases dir missing: $cases_dir — skipping"
        return 0
    fi
    local args="--cases $cases_dir --tier $TIER"
    [ -n "$LANG_ARG_DIFF" ] && args="$args $LANG_ARG_DIFF"
    [ -n "$TAG_ARG_DIFF" ] && args="$args $TAG_ARG_DIFF"
    # shellcheck disable=SC2086
    python3 "$DIFF_HARNESS" $args
}

run_negative() {
    local args=""
    [ -n "$LANG_ARG_NEGATIVE" ] && args="$args $LANG_ARG_NEGATIVE"
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_negative.sh" $args
}

run_nested() {
    local args="$LANG_ARG_NESTED"
    # Phase 9 has only Core tier (curated); smoke == core == full.
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_nested.sh" $args
}

run_perm() {
    local args="--tier=$TIER"
    [ -n "$LANG_ARG_PERM" ] && args="$args $LANG_ARG_PERM"
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_perm.sh" $args
}

run_stmt_pair() {
    local args="--tier=$TIER"
    [ -n "$LANG_ARG_STMT_PAIR" ] && args="$args $LANG_ARG_STMT_PAIR"
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_stmt_pair.sh" $args
}

run_ctrl_flow() {
    local args="--tier=$TIER"
    [ -n "$LANG_ARG_CTRL_FLOW" ] && args="$args $LANG_ARG_CTRL_FLOW"
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_ctrl_flow.sh" $args
}

run_shadow() {
    local args="--tier=$TIER"
    [ -n "$LANG_ARG_SHADOW" ] && args="$args $LANG_ARG_SHADOW"
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_shadow.sh" $args
}

run_hsm_cross() {
    local args="--tier=$TIER"
    [ -n "$LANG_ARG_HSM_CROSS" ] && args="$args $LANG_ARG_HSM_CROSS"
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_hsm_cross.sh" $args
}

run_state_args() {
    local args="--tier=$TIER"
    [ -n "$LANG_ARG_STATE_ARGS" ] && args="$args $LANG_ARG_STATE_ARGS"
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_state_args.sh" $args
}

run_pushpop() {
    local args="--tier=$TIER"
    [ -n "$LANG_ARG_PUSHPOP" ] && args="$args $LANG_ARG_PUSHPOP"
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_pushpop.sh" $args
}

run_multievent() {
    local args="--tier=$TIER"
    [ -n "$LANG_ARG_MULTIEVENT" ] && args="$args $LANG_ARG_MULTIEVENT"
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_multievent.sh" $args
}

run_comments() {
    local args="--tier=$TIER"
    [ -n "$LANG_ARG_COMMENTS" ] && args="$args $LANG_ARG_COMMENTS"
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_comments.sh" $args
}

run_const_sys() {
    local args="--tier=$TIER"
    [ -n "$LANG_ARG_CONST_SYS" ] && args="$args $LANG_ARG_CONST_SYS"
    # shellcheck disable=SC2086
    "$SCRIPT_DIR/run_const_sys.sh" $args
}

# Iterate phases. Don't bail on first failure — surface every phase
# result so the run shows the full picture.
overall_status=0
declare -a PHASE_RESULTS
for p in $PHASES; do
    if run_phase "$p"; then
        PHASE_RESULTS+=("$p:PASS")
    else
        PHASE_RESULTS+=("$p:FAIL")
        overall_status=1
    fi
done

echo ""
echo "============================================================"
echo "run_all.sh summary — tier=$TIER lang=${LANG:-all}"
echo "============================================================"
for r in "${PHASE_RESULTS[@]}"; do
    p=${r%%:*}
    s=${r##*:}
    printf "  Phase %2s (%s): %s\n" "$p" "$(phase_name "$p")" "$s"
done

exit $overall_status
