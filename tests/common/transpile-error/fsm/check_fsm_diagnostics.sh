#!/bin/bash
#
# Negative @@fsm diagnostic suite (issue #20).
#
# @@fsm diagnostics are raised in the validator, BEFORE codegen — they are
# target-independent, so this suite runs on ONE target (python_3) rather than
# ×17. That keeps the matrix cheap while still giving the end-to-end guarantee
# the positive fsm fixtures give for behavior: "framec never emits code that
# doesn't compile" — invalid input must ERROR (with the right code), not
# silently miscompile (the class of bug framec#100 was).
#
# Each fixture declares its expectation in a header comment:
#   # expect-error: E732   → framec must fail AND the emitted error contains E732
#   # expect-ok            → framec must succeed (positive control)
#
# Usage:  ./check_fsm_diagnostics.sh
#         FRAMEC=/path/to/framec ./check_fsm_diagnostics.sh
# Output: TAP. Exit 0 if all pass, 1 otherwise.

set -o pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# framec: prefer the authoritative local build, fall back to PATH.
FRAMEC="${FRAMEC:-$HOME/.frame/local/bin/framec}"
[ -x "$FRAMEC" ] || FRAMEC="$(command -v framec 2>/dev/null)"
if [ -z "$FRAMEC" ] || [ ! -x "$FRAMEC" ]; then
    echo "Bail out! framec not found (set FRAMEC=/path/to/framec)"
    exit 2
fi

fixtures=("$SCRIPT_DIR"/*.fpy)
echo "TAP version 14"
echo "1..${#fixtures[@]}"

n=0
fails=0
for f in "${fixtures[@]}"; do
    n=$((n + 1))
    name="$(basename "$f" .fpy)"

    # Parse the expectation from the first 10 lines.
    expect_code=$(head -10 "$f" | sed -nE 's/^#[[:space:]]*expect-error:[[:space:]]*(E[0-9]{3}).*/\1/p' | head -1)
    expect_ok=$(head -10 "$f" | grep -qE '^#[[:space:]]*expect-ok' && echo yes)

    out="$("$FRAMEC" compile -l python_3 -o /tmp "$f" 2>&1)"
    status=$?

    if [ -n "$expect_ok" ]; then
        if [ $status -eq 0 ]; then
            echo "ok $n - $name (expect-ok: compiled clean)"
        else
            echo "not ok $n - $name (expect-ok but framec rejected it)"
            echo "  ---"; echo "$out" | sed 's/^/  # /' | head -4; echo "  ..."
            fails=$((fails + 1))
        fi
        continue
    fi

    if [ -z "$expect_code" ]; then
        echo "not ok $n - $name (no 'expect-error: EXXX' or 'expect-ok' header)"
        fails=$((fails + 1))
        continue
    fi

    if [ $status -eq 0 ]; then
        echo "not ok $n - $name (expected $expect_code, but framec ACCEPTED it — silent miscompile)"
        fails=$((fails + 1))
    elif echo "$out" | grep -q "$expect_code"; then
        echo "ok $n - $name (rejected with $expect_code)"
    else
        got=$(echo "$out" | grep -oE 'E[0-9]{3}' | head -1)
        echo "not ok $n - $name (expected $expect_code, got ${got:-<no code>})"
        echo "  ---"; echo "$out" | sed 's/^/  # /' | head -4; echo "  ..."
        fails=$((fails + 1))
    fi
done

echo "# fsm diagnostics: $((n - fails)) passed, $fails failed of $n"
[ $fails -eq 0 ]
