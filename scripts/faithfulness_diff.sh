#!/usr/bin/env bash
# FAITHFULNESS GATE — legacy framec is the ground-truth oracle; framec-ng (cleanroom)
# must reproduce its output. For every positive fixture x ng-supported target, emit with
# BOTH and byte-compare. Any divergence is a faithfulness bug. Reports the per-target
# faithfulness rate (% byte-identical to legacy) and saves the divergent fixture list.
#
# This is the ratchet Mark asked for: "we need to be completely faithful to legacy behavior;
# the test env better catch that you aren't." It starts low (the cleanroom stubbed the runtime)
# and must climb to 100% as ng is made faithful.
#
#   FR=<legacy framec>   NG=<framec-ng>   bash scripts/faithfulness_diff.sh
set -uo pipefail
FR="${FR:-$HOME/.frame/local/bin/framec}"   # ORACLE = the latest LOCAL build (4.6.0.x), owner-directed
NG="${NG:-/Users/marktruluck/projects/framec-cleanroom/target/release/framec-ng}"
TE="${TE:-$(cd "$(dirname "$0")/.." && pwd)}"
OUT="${OUT:-/tmp/faithfulness}"
export FRAME_RUNTIME_PY_DIR="${FRAME_RUNTIME_PY_DIR:-$HOME/.frame/local/runtime/py}"
[ -x "$FR" ] || { echo "legacy framec not at $FR"; exit 2; }
[ -x "$NG" ] || { echo "framec-ng not at $NG (cargo build --release --bin framec-ng)"; exit 2; }
mkdir -p "$OUT"; rm -f "$OUT"/*.divergent
# INTENTIONAL DIVERGENCES — fixtures where ng is deliberately NOT byte-identical because it
# FIXES a legacy bug (owner ruling: legacy's bugs are fixed in ng, not reproduced). Each entry
# MUST name the bug and be guarded by a validating runtime fixture in the cleanroom (a test that
# would FAIL on legacy and PASSES on ng). These are reported separately and excluded from the
# faithfulness denominator — they can never go byte-identical, by design.
#   Format: one `<subpath-under-positive/>  # <legacy bug it fixes>` per line.
DIVERGE_LIST="${DIVERGE_LIST:-$TE/scripts/intentional_divergences.txt}"
OOS_LIST="${OOS_LIST:-$TE/scripts/out_of_scope.txt}"
is_oos() { [ -f "$OOS_LIST" ] || return 1; while IFS= read -r p; do case "$p" in "#"*|"") ;; *) case "$1" in $p*) return 0;; esac;; esac; done < "$OOS_LIST"; return 1; }
is_intentional() {  # $1 = fixture subpath
  [ -f "$DIVERGE_LIST" ] || return 1
  grep -vE '^\s*(#|$)' "$DIVERGE_LIST" 2>/dev/null | awk '{print $1}' | grep -qxF "$1"
}
legt() { case "$1" in python) echo python_3;; *) echo "$1";; esac; }   # legacy target name
ext()  { case "$1" in python) echo fpy;; rust) echo frs;; java) echo fjava;; c) echo fc;; esac; }
oext() { case "$1" in python) echo py;;  rust) echo rs;;  java) echo java;;  c) echo c;; esac; }

grand_ok=0; grand_tot=0
tmp=$(mktemp -d)
for t in python rust java c; do
  e=$(ext "$t"); oe=$(oext "$t"); lt=$(legt "$t")
  ident=0; diverg=0; legfail=0; ngfail=0; total=0; intentional=0
  : > "$OUT/$t.divergent"
  while IFS= read -r f; do
    head -10 "$f" 2>/dev/null | grep -qE '@@xfail|@xfail|@@skip|@skip' && continue
    is_oos "${f##*/positive/}" && continue   # parked/out-of-scope (fsm, R5): excluded from denominator
    total=$((total+1))
    # a deliberately-better fixture (ng fixes a legacy bug) is not a faithfulness failure
    if is_intentional "${f##*/positive/}"; then intentional=$((intentional+1)); continue; fi
    rm -rf "$tmp/leg"; mkdir -p "$tmp/leg"
    if ! "$FR" compile -l "$lt" -o "$tmp/leg" "$f" >/dev/null 2>&1; then legfail=$((legfail+1)); continue; fi
    legout=$(ls "$tmp/leg"/*."$oe" 2>/dev/null | head -1)
    [ -f "$legout" ] || { legfail=$((legfail+1)); continue; }
    if ! "$NG" -l "$t" --emit "$f" > "$tmp/ng.$oe" 2>/dev/null; then ngfail=$((ngfail+1)); continue; fi
    if cmp -s "$legout" "$tmp/ng.$oe"; then ident=$((ident+1))
    else diverg=$((diverg+1)); echo "${f##*/positive/}" >> "$OUT/$t.divergent"; fi
  done < <(find "$TE/tests/common/positive" -name "*.$e" | sort)
  runnable=$((ident+diverg))
  pct=$(awk "BEGIN{ if($runnable>0) printf \"%.1f\", 100*$ident/$runnable; else print \"0\" }")
  echo "TARGET $t: fixtures=$total  legacy-emitted=$runnable  BYTE-IDENTICAL=$ident ($pct%)  divergent=$diverg  intentional-divergence=$intentional  (legacy-noemit=$legfail ng-noemit=$ngfail)"
  grand_ok=$((grand_ok+ident)); grand_tot=$((grand_tot+runnable))
done
rm -rf "$tmp"
gp=$(awk "BEGIN{ if($grand_tot>0) printf \"%.1f\", 100*$grand_ok/$grand_tot; else print \"0\" }")
echo "----"
echo "FAITHFULNESS (byte-identical to legacy): $grand_ok / $grand_tot ($gp%)"
echo "divergent lists in $OUT/*.divergent"
