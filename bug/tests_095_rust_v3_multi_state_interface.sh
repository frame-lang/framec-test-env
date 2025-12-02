#!/usr/bin/env bash
set -euo pipefail

# Bug 095 regression: Rust V3 multi-state interface must not generate
# duplicate methods. This script uses the reference framec binary to
# compile a minimal reproducer and then compiles the generated Rust with
# rustc.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRAMEC_BIN="${FRAMEC_BIN:-$ROOT_DIR/releases/frame_transpiler/v0.86.61/framec}"

TMP_DIR="/tmp/bug_095_rust_v3_multi_state_interface"
rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

cat > "$TMP_DIR/test_states.frs" << 'FRM'
@target rust

system S {
    interface:
        run()

    machine:
        $A {
            run() { println!("A"); }
        }
        $B {
            run() { println!("B"); }
        }
}
FRM

"$FRAMEC_BIN" compile -l rust "$TMP_DIR/test_states.frs" -o "$TMP_DIR/out"

RUST_SRC="$TMP_DIR/out/test_states.rs"
if [ ! -f "$RUST_SRC" ]; then
  echo "BUG095_FAIL: generated Rust source not found: $RUST_SRC" >&2
  exit 1
fi

if ! rustc "$RUST_SRC" --crate-type lib -O -o "$TMP_DIR/test_states.rlib"; then
  echo "BUG095_FAIL: rustc compilation failed for generated Rust" >&2
  exit 1
fi

echo "BUG095_OK"
