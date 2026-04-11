#!/bin/bash
# collect-results.sh — Wait for parallel test containers and report results
# Usage: collect-results.sh lang1 lang2 ... langN

set -uo pipefail

LANGS="$@"
COMPOSE="docker compose"
TOTAL_PASS=0
TOTAL_FAIL=0
FAILURES=""

# Wait for all containers to finish
echo "Waiting for $(echo $LANGS | wc -w | tr -d ' ') containers..."
while true; do
    running=0
    still=""
    for lang in $LANGS; do
        state=$($COMPOSE ps --format "{{.State}}" "$lang" 2>/dev/null)
        if [ "$state" = "running" ]; then
            running=$((running + 1))
            still="$still $lang"
        fi
    done
    if [ "$running" -eq 0 ]; then
        break
    fi
    printf "\r  %d running:%s    " "$running" "$still"
    sleep 3
done
printf "\r%80s\r" ""

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
