#!/bin/bash
# collect-results.sh — Wait for parallel test containers and report results
# Usage: collect-results.sh lang1 lang2 ... langN

set -uo pipefail

LANGS="$@"
COMPOSE="docker compose"
TOTAL_PASS=0
TOTAL_FAIL=0
FAILURES=""

# Wait for all containers to finish.
# `docker wait` blocks on the daemon's event stream (push-based, not
# polling) until each container exits. Outer `timeout` bounds the
# worst case — Docker Desktop on macOS has wedged for hours in the
# past, freezing the previous `compose ps` polling loop indefinitely.
# Trade-off: no live "N running:" indicator; we get it back later as
# a separately-bounded best-effort progress reporter if missed.
echo "Waiting for $(echo $LANGS | wc -w | tr -d ' ') containers..."
cids=()
for lang in $LANGS; do
    cid=$($COMPOSE ps -q "$lang" 2>/dev/null) || continue
    [ -n "$cid" ] && cids+=("$cid")
done
if [ "${#cids[@]}" -gt 0 ]; then
    timeout 1800 docker wait "${cids[@]}" >/dev/null || \
        echo "WARNING: docker wait timed out after 30 min or daemon unresponsive"
fi

echo ""
echo "=========================================="
echo "Results"
echo "=========================================="

# Collect results per language
for lang in $LANGS; do
    summary=$($COMPOSE logs --no-log-prefix "$lang" 2>/dev/null | grep "^# " | tail -1)
    lang_failures=$($COMPOSE logs --no-log-prefix "$lang" 2>/dev/null | grep "^not ok ")

    if [ -n "$lang_failures" ]; then
        FAILURES="$FAILURES$lang_failures"$'\n'
        TOTAL_FAIL=$((TOTAL_FAIL + 1))
    else
        TOTAL_PASS=$((TOTAL_PASS + 1))
    fi

    echo "$summary"
done

# Print failures at the end for visibility
if [ -n "$FAILURES" ]; then
    echo ""
    echo "=========================================="
    echo "Failures"
    echo "=========================================="
    echo "$FAILURES"
fi

echo "=========================================="
echo "$TOTAL_PASS languages clean, $TOTAL_FAIL with failures"
if [ "$TOTAL_FAIL" -gt 0 ]; then
    exit 1
fi
