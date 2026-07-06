#!/usr/bin/env bash
# Phase 26 — async × persist fuzz.
#
# Generates the cross-product cases with gen_async_persist.py (11 async
# backends × 4 patterns: await_then_save, save_between_awaits,
# restore_then_await, gate_clears) and checks that framec **transpiles** every
# one. That is the fuzz value here: the async×persist codegen seam (the async
# casing's transient gate + `_<Name>Machine` split × the persist serializer)
# is exactly where a codegen regression would surface as a transpile failure
# or a wrong-code rejection.
#
# Transpile-only by design. The generated code's compile + runtime round-trip
# is covered end-to-end by the matrix's `async_persist_roundtrip_gate_clears`
# fixtures on all 11 backends (persist needs per-language JSON libs — serde /
# Jackson / cjson / nlohmann — that this fuzz layer doesn't provision).
#
# TAP output. Usage: ./run_async_persist.sh [--tier=smoke|core|full] [--lang=<name> ...]

set -o pipefail
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
FRAMEC=${FRAMEC:-$(command -v framec 2>/dev/null)}
CASES_DIR=$SCRIPT_DIR/cases_async_persist

TIER="full"
EXPLICIT_LANGS=""
while [ $# -gt 0 ]; do
    case "$1" in
        --tier=*) TIER="${1#--tier=}" ;;
        --tier) shift; TIER="$1" ;;
        --lang=*) EXPLICIT_LANGS="${EXPLICIT_LANGS} ${1#--lang=}" ;;
        --lang) shift; EXPLICIT_LANGS="${EXPLICIT_LANGS} $1" ;;
        --help|-h) echo "Usage: $0 [--tier=smoke|core|full] [--lang=<name> ...]"; exit 0 ;;
        *) EXPLICIT_LANGS="${EXPLICIT_LANGS} $1" ;;
    esac
    shift || true
done

if [ -z "$FRAMEC" ] || [ ! -x "$FRAMEC" ]; then
    echo "Bail out! framec not found (set FRAMEC=/path/to/framec)"; exit 2
fi

# tier → cases per (pattern × backend)
case "$TIER" in smoke) MAX=1 ;; core) MAX=2 ;; *) MAX=3 ;; esac

# ext → framec target (case, not an assoc array — macOS ships bash 3.2, which
# lacks `declare -A`, and `#!/usr/bin/env bash` can resolve to it).
ext_target() {
    case "$1" in
        fpy) echo python_3 ;; fts) echo typescript ;; fjs) echo javascript ;;
        frs) echo rust ;;     fcpp) echo cpp_23 ;;   fcs) echo csharp ;;
        fjava) echo java ;;   fkt) echo kotlin ;;    fswift) echo swift ;;
        fdart) echo dart ;;   fgd) echo gdscript ;;  *) echo "" ;;
    esac
}
lang_wanted() {
    [ -z "$EXPLICIT_LANGS" ] && return 0
    for l in $EXPLICIT_LANGS; do [ "$l" = "$1" ] && return 0; done
    return 1
}

rm -rf "$CASES_DIR"
python3 "$SCRIPT_DIR/gen_async_persist.py" --max "$MAX" --out-dir "$CASES_DIR" >/dev/null 2>&1

W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
num=0; pass=0; fail=0
echo "TAP version 14"

for case_file in "$CASES_DIR"/*; do
    [ -f "$case_file" ] || continue
    ext="${case_file##*.}"; name="$(basename "$case_file" ".$ext")"
    target="$(ext_target "$ext")"; [ -n "$target" ] || continue
    lang_wanted "$target" || continue
    num=$((num + 1))
    if "$FRAMEC" compile -l "$target" -o "$W" "$case_file" >"$W/err" 2>&1; then
        echo "ok $num - $name"
        pass=$((pass + 1))
    else
        echo "not ok $num - $name # transpile failed: $(grep -iE 'error|E[0-9]{3}' "$W/err" | head -1 | cut -c1-70)"
        fail=$((fail + 1))
    fi
done

echo "1..$num"
echo "# async×persist transpile (tier=$TIER, max=$MAX): $pass passed, $fail failed of $num"
[ "$fail" -eq 0 ]
