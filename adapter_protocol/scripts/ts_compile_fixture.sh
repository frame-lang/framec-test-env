#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
FRAMEC_BIN="${FRAMEC_BIN:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"
TS_BIN="$ROOT/node_modules/.bin/tsc"

if [ $# -lt 1 ]; then
  echo "usage: $(basename "$0") <fixture.frm>" >&2
  exit 2
fi
FIXTURE_PATH="$1"
if [ ! -f "$FIXTURE_PATH" ]; then
  echo "error: fixture not found: $FIXTURE_PATH" >&2
  exit 2
fi

if [ ! -x "$TS_BIN" ]; then
  echo "error: TypeScript compiler not found at $TS_BIN" >&2
  exit 2
fi

OUT_DIR="$(mktemp -d)"
"$FRAMEC_BIN" --version || true
"$FRAMEC_BIN" compile -l typescript -o "$OUT_DIR" "$FIXTURE_PATH"

cat > "$OUT_DIR/tsconfig.json" <<JSON
{
  "compilerOptions": {
    "target": "es2019",
    "module": "commonjs",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "baseUrl": ".",
    "paths": { "frame_runtime_ts": ["$ROOT/runtime/frame_runtime_ts.d.ts"] },
    "outDir": "./out"
  },
  "files": ["$(basename "$FIXTURE_PATH" .frm).ts", "$ROOT/runtime/frame_runtime_ts.d.ts"]
}
JSON

set +e
"$TS_BIN" -p "$OUT_DIR/tsconfig.json"
RC=$?
set -e

if [ $RC -eq 0 ]; then
  echo "TS_COMPILE_OK: $(basename "$FIXTURE_PATH")"
  exit 0
else
  echo "TS_COMPILE_FAIL: $(basename "$FIXTURE_PATH")" >&2
  exit 1
fi

