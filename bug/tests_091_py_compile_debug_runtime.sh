#!/usr/bin/env bash
set -euo pipefail

# Bug 091 shared-env validation: ensure PythonDebugRuntime.py is syntactically valid.
# This is expected to FAIL until the FRM/source is fixed and the artifact regenerated.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${ROOT}/bug/artifacts/091/PythonDebugRuntime.py"

if [[ ! -f "${TARGET}" ]]; then
  echo "Missing artifact: ${TARGET}" >&2
  exit 1
fi

python3 -m py_compile "${TARGET}"
echo "PY_COMPILE_OK"
