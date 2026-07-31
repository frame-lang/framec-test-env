#!/usr/bin/env bash
# Present framec-ng's CLI on top of the LEGACY 4.6.0.33 oracle, so `golden_run.py` can judge the
# oracle with the byte-for-byte identical gate it applies to ng.
#
#   NG=scripts/framec-oracle-shim.sh python3 scripts/golden_run.py rust --all
#
# WHY THIS EXISTS. The corpus has been validated by comparing ng's BYTES to the oracle's. That
# cannot see a bug the oracle itself has -- and it has several proved ones (a lexer that
# double-encodes every non-ASCII string literal; a pass that silently deletes user code after a
# `return;`; two divergent hardcoded "is this type Copy?" tables driving `.clone()` insertion).
# Byte-matching a buggy oracle reproduces the bug and reports success.
#
# Running the ORACLE through EMIT -> BUILD -> RUN -> ASSERT turns each of those into a fixture
# FAILURE, which is the only form in which they can enter a worklist. Everything downstream of
# `emit()` in golden_run.py is already compiler-agnostic -- it only ever sees a file on disk -- so
# this argv adapter is the entire missing mechanism.
#
# The two CLIs differ only in argv and target spelling; the oracle already writes a single file to
# stdout, so no temp dir is needed:
#
#   ng      framec-ng -l rust --emit F   -> stdout
#   oracle  framec    -l rust        F   -> stdout   (identical to its `-o DIR` file, modulo a
#                                                     trailing newline)
#
# It is deliberately NOT the mirror of `framec-ng-shim.sh`, which adapts the other direction
# (legacy CLI in, ng out) and is used for the docker matrix.
set -euo pipefail

FR="${FR:-$HOME/.frame/local/bin/framec}"

[ -x "$FR" ] || { echo "framec-oracle-shim: oracle not executable: $FR" >&2; exit 2; }

target=""
file=""
while [ $# -gt 0 ]; do
    case "$1" in
        -l)     target="$2"; shift 2 ;;
        --emit) shift ;;          # ng-only flag; the oracle emits to stdout by default
        -*)     echo "framec-oracle-shim: unsupported flag: $1" >&2; exit 2 ;;
        *)      file="$1"; shift ;;
    esac
done

[ -n "$target" ] || { echo "framec-oracle-shim: no -l <target>" >&2; exit 2; }
[ -n "$file" ]   || { echo "framec-oracle-shim: no input file" >&2; exit 2; }

# The oracle spells python differently. Refuse anything golden_run cannot BUILD, rather than
# emitting code no stage will ever check -- a silent pass is the failure mode this whole exercise
# is trying to remove.
case "$target" in
    python) legacy_target="python_3" ;;
    rust|c|java) legacy_target="$target" ;;
    *) echo "framec-oracle-shim: target '$target' has no build stage in golden_run.py" >&2; exit 2 ;;
esac

exec "$FR" -l "$legacy_target" "$file"
