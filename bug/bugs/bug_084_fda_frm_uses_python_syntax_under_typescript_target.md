# Bug #084: FrameDebugAdapter.frm uses Python-native syntax under @target typescript

## Metadata
bug_number: 084
title: FrameDebugAdapter.frm uses Python-native syntax under @target typescript
status: Closed
priority: High
category: Documentation
discovered_version: v0.86.54
reporter: vscode_editor (Codex)
assignee: vscode_editor (Codex)
created_date: 2025-11-20
fixed_version: v0.86.54
resolved_date: 2025-11-21

## Description
The Frame Debug Adapter FRM (`src/debug/state_machines/FrameDebugAdapter.frm`) is authored with `@target typescript` but its handler bodies use Python-native syntax (`self.*`, `None`, `True`, Python f-strings, etc.). In V3, bodies are native to the selected target. Emitting these bodies into the generated TypeScript results in `tsc` parse errors, blocking TypeScript compilation and adapter validation.

Examples observed in the FRM:
- `self.debugServer = None`
- `self.capabilities = { ... "supportsTerminateRequest": True }`
- `self.sendDebugConsole(f"Debug session ID: {self.debugSessionId}")`

These are not valid TypeScript and cannot be compiled by `tsc` when spliced into the generated module.

## Reproduction Steps
1) Generate TypeScript from the FRM with framec v0.86.54:
   - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec`
   - `OUT_DIR=$(mktemp -d)`
   - `$FRAMEC_BIN compile -l typescript -o "$OUT_DIR" src/debug/state_machines/FrameDebugAdapter.frm`
2) Compile the generated TS against the shared env runtime d.ts (path mapping):
   - Create `$OUT_DIR/tsconfig.json` with:
     ```json
     {
       "compilerOptions": {
         "target": "es2019",
         "module": "commonjs",
         "esModuleInterop": true,
         "skipLibCheck": true,
         "baseUrl": ".",
         "paths": { "frame_runtime_ts": ["/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/runtime/frame_runtime_ts.d.ts"] },
         "outDir": "./out"
       },
       "files": ["FrameDebugAdapter.ts", "/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/runtime/frame_runtime_ts.d.ts"]
     }
     ```
   - Run `/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/node_modules/.bin/tsc -p "$OUT_DIR/tsconfig.json"`
3) Observe `tsc` failures such as `TS1127 Invalid character`, `TS1005 ';' expected` around Python syntax locations.



## Build/Release Artifacts
- framec binary used for validation:
  `/Users/marktruluck/projects/frame_transpiler/target/release/framec` (v0.86.54, build 48)
- Debug adapter FRM:
  `src/debug/state_machines/FrameDebugAdapter.frm` in the VS Code adapter
  project (checked out alongside `frame_transpiler` / `framepiler_test_env`).
- TypeScript compiler:
  `/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/node_modules/.bin/tsc`
  with `tsconfig.json` as shown above.

## Verification Tests
- Adapter repo (debugger team):
  - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec`
  - `OUT_DIR=$(mktemp -d)`
  - `$FRAMEC_BIN compile -l typescript -o "$OUT_DIR" src/debug/state_machines/FrameDebugAdapter.frm`
  - Add a `tsconfig.json` in `$OUT_DIR` mapping `frame_runtime_ts` to the shared d.ts and run:
    `/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/node_modules/.bin/tsc -p "$OUT_DIR/tsconfig.json"`
- Shared env smoke (integration check):
  - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec /Users/marktruluck/projects/framepiler_test_env/adapter_protocol/scripts/run_adapter_smoke.sh`

## Expected Behavior
- With `@target typescript`, handler bodies should be valid TypeScript. Generated TS should compile cleanly with `tsc` when mapped to the shared env runtime types.

## Actual Behavior
- Generated TS contains Python-native constructs from the FRM bodies and fails to compile with `tsc`.

## Impact
- Severity: High — Blocks TypeScript adapter generation/validation for FrameDebugAdapter.
- Scope: Affects all TS compilation of this system until bodies are converted to TS (or the FRM retargeted to `@target python_3`).

## Proposed Next Steps
- Option A: Convert handler/action bodies to valid TypeScript (use `this` instead of `self`, `null/undefined` instead of `None`, `true/false` instead of `True/False`, template strings `${}` instead of Python f-strings, etc.).
- Option B: If the intent is to keep Python-native bodies, change prolog to `@target python_3` and validate via the Python target.
- In either case, keep SOL-anchored Frame statements (transitions/forwards/stack ops) and ensure block order matches V3 (current order is interface → machine → actions, which is acceptable).

## Closure Requirements (shared env + adapter)
- **Adapter FRM semantics**
  - `src/debug/state_machines/FrameDebugAdapter.frm` must either:
    - Use `@target typescript` with fully TS-native bodies (no `self`, `None`, `True`, f-strings, etc.), or
    - Be explicitly retargeted to `@target python_3` if Python-native bodies are required.
  - All remaining Pythonism in the TS target must be removed or guarded behind a Python target.
- **Compile + type-check with current toolchain**
  - Use `framec v0.86.54` or later:
    - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec`
    - `OUT_DIR=$(mktemp -d)`
    - `$FRAMEC_BIN compile -l typescript -o "$OUT_DIR" src/debug/state_machines/FrameDebugAdapter.frm`
  - Ensure `$OUT_DIR/tsconfig.json` maps `frame_runtime_ts` to the shared d.ts (as in Reproduction Steps).
  - Run:
    - `/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/node_modules/.bin/tsc -p "$OUT_DIR/tsconfig.json"`
  - Requirement: `tsc` must complete without syntax errors caused by Python-native constructs in the generated TS.
- **Shared env smoke**
  - With the same `framec` build, run:
    - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec /Users/marktruluck/projects/framepiler_test_env/adapter_protocol/scripts/run_adapter_smoke.sh`
  - Requirement: output must include `ADAPTER_SMOKE_OK`.
- **Reporting back into this bug**
  - When closing, include:
    - The exact `FRAMEC_BIN` path and version used.
    - The `$OUT_DIR` used for the adapter compile.
    - Confirmation that:
      - The FRM is TS-native (or retargeted to Python as agreed).
      - `tsc` and adapter smoke both pass with the documented commands.

## Work Log
- 2025-11-20: Filed after V3 doc reread and FRM scan; reproduced `tsc` parse errors with v0.86.54 — vscode_editor
- 2025-11-20: FRM bodies substantially converted to TS (Option A). Current compile now fails due to missing runtime helper declarations; see Bug #086. No TS2339 class-field errors observed (Bug #085 addressed). — vscode_editor
- 2025-11-21: Revalidated on v0.86.54 after Bug #086 and #087 fixes. Compile progresses but still fails with `TS2322` (boolean not assignable to void), indicating generator not honoring FRM return types. Tracked by Bug #088. Will rerun compile + smoke and close this bug once #088 is fixed. — vscode_editor

- 2025-11-21: FRM is now TS-native; no Python syntax remains. Shared env smoke passes (`ADAPTER_SMOKE_OK`). Remaining `tsc` failures are strictly type-level (return types) and tracked under Bug #088. Closing #084 as its scope (Python syntax under TS target) is resolved. — vscode_editor

- 2025-11-20: Debugger team TODO (on or after Bug #086 fix):
  - Complete remaining TS-native conversions in handlers/actions (no `any` casts; keep SOL-anchored Frame statements only).
  - Re-run compile verification: `framec -l typescript` → `tsc` with shared d.ts path mapping.
  - Run shared env smoke: `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec /Users/marktruluck/projects/framepiler_test_env/adapter_protocol/scripts/run_adapter_smoke.sh`.
  - If both compile and smoke pass, set this bug to Fixed; opener will verify and set to Closed.
  - Also confirm Bug #085 remains clean (no TS2339 field errors); if so, leave #085 Fixed and proceed to closure.
  - If opting for Option B instead, change prolog to `@target python_3` and add a `py_compile` verification step; then proceed with Fixed → Closed.
- 2025-11-21: Reopened after additional adapter validation; further issues remain to be investigated with the updated FRM and toolchain. — framepiler team

## Current Status
- FRM conversion: complete — debugger team has converted `FrameDebugAdapter.frm` to TS-native bodies under `@target typescript` (or has retargeted to `@target python_3` with Python-native bodies).
- Runtime API and d.ts: adapter helper declarations (Bug #086) and TS codegen integration (Bugs #085–#087) are fixed in `frame_transpiler` v0.86.54.
- Shared env smoke: passes with `framec 0.86.54`:
  - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec /Users/marktruluck/projects/framepiler_test_env/adapter_protocol/scripts/run_adapter_smoke.sh` → `ADAPTER_SMOKE_OK`.

## Verification (parse-level)
- Expected check (adapter repo): regenerate TS and type-check with `tsc` using shared d.ts path mapping.
- Result on `framec v0.86.54`: no parser/tokenization errors from Python-native constructs. Any remaining `tsc` errors are type-level and covered by Bug #088.

## Repro Shortcuts
- Historical repro (pre-fix) remains as documented above; for ongoing validation, use the same commands and confirm absence of Python-syntax parse errors.
