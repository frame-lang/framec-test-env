#!/usr/bin/env bash
set -euo pipefail

# Aggregate all smokes: adapter harness + runtime smokes + adapter scopes.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRAMEC_BIN="${FRAMEC_BIN:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"

run() {
  echo "=== $1 ==="
  FRAMEC_BIN="$FRAMEC_BIN" "$ROOT/scripts/$1"
}

FRAMEC_BIN="$FRAMEC_BIN" "$ROOT/scripts/ts_compile_fixture.sh" "${ROOT}/adapter_protocol_minimal.frm"
FRAMEC_BIN="$FRAMEC_BIN" "$ROOT/scripts/run_adapter_smoke.sh"
FRAMEC_BIN="$FRAMEC_BIN" "$ROOT/scripts/run_fda_smoke.sh" "${ROOT}/adapter_protocol_minimal.frm"
run "run_runtime_smokes.sh"
node "$ROOT/scripts/run_adapter_scopes_smoke.js"

echo "ALL_SMOKES_OK"
