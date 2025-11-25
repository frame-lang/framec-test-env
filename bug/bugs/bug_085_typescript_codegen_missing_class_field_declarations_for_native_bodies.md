# Bug #085: TypeScript codegen missing class field declarations for native bodies

## Metadata
bug_number: 085
title: TypeScript codegen missing class field declarations for native bodies
status: Closed
priority: High
category: CodeGen
discovered_version: v0.86.54
reporter: vscode_editor (Codex)
assignee: framepiler team
created_date: 2025-11-20
resolved_date: 2025-11-20
fixed_version: v0.86.54

## Description
When compiling a V3 system with `@target typescript`, the generator emits a TS class but does not declare fields that are referenced or assigned in the native bodies (FRM handlers/actions). As a result, `tsc` reports property-missing errors (TS2339) for every such field (e.g., `frameFile`, `capabilities`, `executionState`, etc.).

This blocks adopting V3’s “native bodies” principle for TS because typical adapter/state-machine code stores mutable state on `this` and expects the class to own these fields.

## Reproduction Steps
1) Use `src/debug/state_machines/FrameDebugAdapter.frm` (adapter repo) which contains native TS bodies with assignments to fields like `this.frameFile`, `this.capabilities`, etc. (converted from Python as part of Option A).
2) Generate TS with framec v0.86.54:
   - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec`
   - `OUT_DIR=$(mktemp -d)`
   - `$FRAMEC_BIN compile -l typescript -o "$OUT_DIR" src/debug/state_machines/FrameDebugAdapter.frm`
3) Compile with the shared env runtime types:
   - Create `$OUT_DIR/tsconfig.json` mapping `frame_runtime_ts` to the shared d.ts
   - Run `/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/node_modules/.bin/tsc -p "$OUT_DIR/tsconfig.json"`
4) Observe errors like:
   - `TS2339: Property 'frameFile' does not exist on type 'FrameDebugAdapter'.`
   - Similar TS2339 for other fields (capabilities, executionState, etc.).

## Expected Behavior
- The generated TS class should declare fields that are referenced/assigned in FRM bodies so that `tsc` can type-check successfully without resorting to `any` casts.

## Actual Behavior
- No class fields are declared; `tsc` emits TS2339 for each property access written in the native FRM bodies.

## Impact
- Severity: High — prevents compiling valid V3 TS systems that maintain state on `this` inside native handler/action bodies.
- Scope: Any TS system that uses native bodies with fields on `this`.

## Proposed Solutions
- Option A (preferred): Synthesize class field declarations from native-body usage (assignments to `this.<ident>`), declared once at the top of the class (e.g., `public frameFile: any;`).
- Option B: Support a `domain:` or `fields:` block whose entries generate TS field declarations (types may be `any` by default or inferable later).
- Option C: Provide a generator flag that emits a permissive index signature (`[k: string]: any`) on the class for V3 TS targets; acceptable as interim but less precise.

## Build/Release Artifacts
- framec: `/Users/marktruluck/projects/frame_transpiler/target/release/framec` (v0.86.54)
- Runtime types: `/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/runtime/frame_runtime_ts.d.ts`
- TypeScript: `/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/node_modules/.bin/tsc`

## Verification Tests
- Add a shared compile test using a minimal fixture that assigns and reads fields on `this`:
  - Fixture: `adapter_protocol/test_fixture_ts_codegen_fields.frm`
  - Command: `bash adapter_protocol/scripts/ts_compile_fixture.sh adapter_protocol/test_fixture_ts_codegen_fields.frm`
  - PASS: `TS_COMPILE_OK` with no TS2339 property errors on fields like `counter`, `stateName`, `settings`.
- The full adapter FRM should also compile once this fix lands.

## Work Log
- 2025-11-20: Filed after converting FDA FRM bodies to TS (Option A). `tsc` shows TS2339 for numerous fields; generator currently emits no member declarations — vscode_editor
- 2025-11-20: Added minimal compile fixture and harness in shared env; fixture compiles OK. Full FDA compile shows no TS2339 field errors; remaining failures are due to runtime d.ts gaps (see Bug #086). Marking this bug Fixed; awaiting closure after opener verification. — vscode_editor


### Debugger Team TODO
- After the runtime typings issues (Bug #086) are resolved:
  - Rebuild and compile the adapter FRM with `framec v0.86.54` and `tsc` using the shared env `tsconfig.json`.
  - Confirm there are no remaining TS2339 "property does not exist" errors for known instance fields (see Field Inventory below).
  - If any TS2339s remain, report the field names here so we can decide whether they should be declared via `domain:`/explicit fields in the FRM or added to the synthesized field set.
- Once the adapter's TS build is clean (aside from any unrelated runtime typing issues), the opener can move this bug from Fixed to Closed.

## Field Inventory (from FRM bodies)
Derived from `src/debug/state_machines/FrameDebugAdapter.frm` assignments to `this.<field>`:

- frameFile
- debugPort
- debugServer
- pythonProcess
- vsCodeSession
- capabilities
- debugSessionId
- framePythonCode
- frameSourceMap
- debugRuntimeCode
- activeBreakpoints
- breakpointIdCounter
- breakpointMap
- sourceMapData
- executionState
- currentFrame
- currentFrameLine
- pauseReason
- stepMode
- stepTargetDepth
- executionThread
- variableReferences
- nextVariableRef
- currentScopes
- frameStack
- variableCache
- callStackFrames
- frameIdCounter
- pythonFrameToFrameId
- frameSystemName
- frameStates
- frameInterfaceMethods

These should be declared as class members in the generated TS for the system.
