#!/usr/bin/env bash
set -euo pipefail

# Aggregate runtime smokes (socket-based): entry, breakpoint, step.
# Requires adapter dist artifacts present (or build_adapter_js.sh in scripts/) and loopback bind permission.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FRAMEC_BIN="${FRAMEC_BIN:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"

run() {
  echo "=== $1 ==="
  FRAMEC_BIN="$FRAMEC_BIN" "$ROOT/scripts/$1"
}

run "run_runtime_smoke_entry.sh"
run "run_runtime_smoke_breakpoint.sh"
run "run_runtime_smoke_step.sh"
run "run_runtime_smoke_step_in_out.sh"
run "run_runtime_smoke_resume.sh"
run "run_runtime_smoke_breakpoint_resume.sh"

echo "RUNTIME_SMOKES_OK"
