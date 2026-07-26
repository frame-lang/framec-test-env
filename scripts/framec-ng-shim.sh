#!/usr/bin/env bash
# framec-ng adapter — presents the legacy `framec compile -l <target> -o <dir> <file>` CLI
# and drives framec-ng (the cleanroom compiler, bin `framec-ng`). The cleanroom CLI differs
# (no `compile` subcommand, no `-o`; it emits to stdout via `--emit`), so this shim bridges it.
#
# It maps the legacy target NAMES to ng's, and REFUSES the 13 targets ng does not implement yet
# (exit 2 -> the test-env harness records a normal fail, so the coverage delta is honest).
#
# Wire it in:   FRAMEC=/abs/path/scripts/framec-ng-shim.sh  tests/run_all_tests.sh <lang>
# ng binary:    override with FRAMEC_NG=/path/to/framec-ng   (default = cleanroom release build)
set -uo pipefail
NG="${FRAMEC_NG:-/Users/marktruluck/projects/framec-cleanroom/target/release/framec-ng}"
[ -x "$NG" ] || { echo "framec-ng-shim: ng binary not found at $NG (build: cargo build --release --bin framec-ng)" >&2; exit 3; }

sub="${1:-}"; shift || true          # expect: compile
target=""; out_dir="."; file=""
while [ $# -gt 0 ]; do
  case "$1" in
    -l|--language) target="${2:-}"; shift 2 ;;
    -o)            out_dir="${2:-.}"; shift 2 ;;
    -*)            shift ;;           # ignore unknown flags
    *)             file="$1"; shift ;;
  esac
done
[ "$sub" = compile ] || { echo "framec-ng-shim: only the 'compile' subcommand is bridged" >&2; exit 2; }
[ -n "$file" ]       || { echo "framec-ng-shim: no input file" >&2; exit 2; }

# legacy target name -> (ng target, output extension)
case "$target" in
  python_3) ngt=python; ext=py ;;
  rust)     ngt=rust;   ext=rs ;;
  java)     ngt=java;   ext=java ;;
  c)        ngt=c;      ext=c ;;
  *) echo "framec-ng-shim: target '$target' is not implemented by framec-ng (supports 4 of 17: python_3, rust, java, c)" >&2; exit 2 ;;
esac

name=$(basename "$file" | sed 's/\.f[a-z0-9_]*$//')
mkdir -p "$out_dir"
out="$out_dir/$name.$ext"
err=$(mktemp)
"$NG" -l "$ngt" --emit "$file" > "$out" 2>"$err"
code=$?
if [ $code -ne 0 ]; then
  cat "$err" >&2          # surface ng's diagnostic
  rm -f "$out" "$err"     # no output file -> harness sees a clean fail
  exit $code
fi
rm -f "$err"
exit 0
