#!/usr/bin/env bash
# DIFFERENTIAL TEST — ng vs legacy, CODE and RESULTS, per fixture.
#
# Owner directive: the tests assert IDENTICAL code output AND IDENTICAL run results, unless we know
# EXACTLY why the delta exists — i.e. the fixture carries a journaled intentional divergence
# (DIVERGENCE-JOURNAL.md, listed in intentional_divergences.txt, with a runtime validator).
#
# For each fixture it runs TWO gates:
#   CODE  : emit with ng and with the legacy oracle (regenerated fresh), `diff`.
#           identical -> ok ; divergent+journaled -> ok(journaled) ; divergent+unjournaled -> FAIL.
#   RESULT: (where runnable) run BOTH emitted programs, compare output.
#           identical -> ok ; divergent+journaled -> ok(journaled, e.g. legacy crashes / ng passes) ;
#           divergent+unjournaled -> FAIL.
#
# An UNJOURNALED delta (code or result) is a hard FAIL: either ng is silently wrong, or an
# intentional change was never recorded. Both are forbidden.
#
#   TARGET=python bash scripts/differential_test.sh [<fixture-subpath> ...]   # default: all in-scope
set -uo pipefail
FR="${FR:-$HOME/.frame/local/bin/framec}"   # ORACLE = the latest LOCAL build (4.6.0.x), owner-directed
NG="${NG:-/Users/marktruluck/projects/framec-cleanroom/target/release/framec-ng}"
TE="${TE:-$(cd "$(dirname "$0")/.." && pwd)}"
TARGET="${TARGET:-python}"
JOURNAL_LIST="${JOURNAL_LIST:-$TE/scripts/intentional_divergences.txt}"
export FRAME_RUNTIME_PY_DIR="${FRAME_RUNTIME_PY_DIR:-$HOME/.frame/local/runtime/py}"
[ -x "$FR" ] || { echo "legacy framec not at $FR"; exit 2; }
[ -x "$NG" ] || { echo "framec-ng not at $NG"; exit 2; }

legt() { case "$1" in python) echo python_3;; *) echo "$1";; esac; }
ext()  { case "$1" in python) echo fpy;; rust) echo frs;; java) echo fjava;; c) echo fc;; esac; }
oext() { case "$1" in python) echo py;;  rust) echo rs;;  java) echo java;;  c) echo c;; esac; }
journaled() { grep -vE '^\s*(#|$)' "$JOURNAL_LIST" 2>/dev/null | awk '{print $1}' | grep -qxF "$1"; }
# run an emitted program, echo its result signature (TAP lines or the error), for RESULT identity
run_out() { case "$TARGET" in
    python) python3 "$1" 2>&1 | grep -E '^(ok|not ok|Traceback|[A-Za-z]+Error)' || echo "<no-tap>";;
    *) echo "<run-skip:$TARGET>";;   # other targets need their toolchain; code gate still applies
  esac; }

e=$(ext "$TARGET"); oe=$(oext "$TARGET"); lt=$(legt "$TARGET")
fixtures=()
if [ "$#" -gt 0 ]; then for s in "$@"; do fixtures+=("$TE/tests/common/positive/$s"); done
else while IFS= read -r p; do fixtures+=("$p"); done < <(find "$TE/tests/common/positive" -name "*.$e" | sort); fi

ok_id=0; ok_j=0; fail_code=0; fail_res=0; tmp=$(mktemp -d)
for f in "${fixtures[@]}"; do
  [ -f "$f" ] || continue
  head -10 "$f" 2>/dev/null | grep -qE '@@xfail|@xfail|@@skip|@skip' && continue
  sub="${f##*/positive/}"
  rm -rf "$tmp/l"; mkdir -p "$tmp/l"
  "$FR" compile -l "$lt" -o "$tmp/l" "$f" >/dev/null 2>&1 || { echo "SKIP  $sub (legacy no-emit)"; continue; }
  legout=$(ls "$tmp/l"/*."$oe" 2>/dev/null | head -1); [ -f "$legout" ] || { echo "SKIP  $sub (legacy no-file)"; continue; }
  "$NG" -l "$TARGET" --emit "$f" > "$tmp/n.$oe" 2>/dev/null || { echo "FAIL  $sub (ng no-emit)"; fail_code=$((fail_code+1)); continue; }
  # --- CODE gate ---
  if cmp -s "$legout" "$tmp/n.$oe"; then code=identical
  elif journaled "$sub"; then code=journaled
  else code=UNJOURNALED; fi
  # --- RESULT gate (best-effort per target) ---
  lr=$(run_out "$legout"); nr=$(run_out "$tmp/n.$oe")
  if [ "$lr" = "$nr" ]; then res=identical
  elif journaled "$sub"; then res=journaled     # e.g. legacy crashes, ng passes (a bug-fix)
  else res=UNJOURNALED; fi
  # --- verdict ---
  case "$code:$res" in
    identical:identical) ok_id=$((ok_id+1));;
    UNJOURNALED:*) echo "FAIL  $sub  CODE unjournaled delta ($(diff "$legout" "$tmp/n.$oe" | grep -c '^[<>]') lines)"; fail_code=$((fail_code+1));;
    *:UNJOURNALED) echo "FAIL  $sub  RESULT unjournaled: legacy=[$lr] ng=[$nr]"; fail_res=$((fail_res+1));;
    *) ok_j=$((ok_j+1)); echo "ok(journaled)  $sub  code=$code result=$res";;
  esac
done
rm -rf "$tmp"
echo "----"
echo "TARGET $TARGET  identical=$ok_id  journaled=$ok_j  FAIL(code-unjournaled)=$fail_code  FAIL(result-unjournaled)=$fail_res"
[ $((fail_code+fail_res)) -eq 0 ]