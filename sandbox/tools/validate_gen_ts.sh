#!/usr/bin/env bash
set -euo pipefail

FRAMEC_BIN="/Users/marktruluck/projects/frame_transpiler/target/release/framec"
OUT_DIR="$(cd "$(dirname "$0")" && pwd)/gen_ts"

rm -rf "$OUT_DIR" && mkdir -p "$OUT_DIR"
"$FRAMEC_BIN" compile -l typescript -o "$OUT_DIR" "$(cd "$(dirname "$0")" && pwd)/adapter_protocol.frm"
cat > "$OUT_DIR/tsconfig.json" <<'JSON'
{
  "compilerOptions": {
    "target": "es2019",
    "module": "commonjs",
    "lib": ["es2019", "dom"],
    "esModuleInterop": true,
    "skipLibCheck": true,
    "baseUrl": "../../",
    "paths": { "frame_runtime_ts": ["frame_runtime_ts/index"] },
    "outDir": "./out"
  },
  "files": ["adapter_protocol.ts"]
}
JSON

echo "Compiling generated TS against workspace runtime types..."
npx -y tsc -p "$OUT_DIR/tsconfig.json"
echo "OK: generated TS compiles cleanly."

