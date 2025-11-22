# Bug #088: TypeScript codegen ignores action return type annotations (void vs boolean/array)

## Metadata
bug_number: 088
title: TypeScript codegen ignores action return type annotations (void vs boolean/array)
status: Closed
priority: High
category: CodeGen
discovered_version: v0.86.54
reporter: vscode_editor (Codex)
assignee: framepiler team
created_date: 2025-11-21
fixed_version: v0.86.54
resolved_date: 2025-11-21

## Description
FRM action/operation headers in the TS target declare explicit return types (e.g., `spawnFramePython(): boolean`). Generated TS methods are still emitted/treated as `void`, which leads to compile errors when the bodies `return true/false` or when calling sites test for truthiness.

## Reproduction Steps
1) Compile the adapter FRM:
   - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec`
   - `OUT_DIR=$(mktemp -d)`
   - `$FRAMEC_BIN compile -l typescript -o "$OUT_DIR" src/debug/state_machines/FrameDebugAdapter.frm`
2) tsc with shared d.ts mapping (path-mapped `frame_runtime_ts`):
   - `/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/node_modules/.bin/tsc -p "$OUT_DIR/tsconfig.json"`
3) Observe errors like:
   - `error TS2322: Type 'boolean' is not assignable to type 'void'.`

## Expected Behavior
- Generated TS method signatures honor declared return types in FRM headers so TS type-check passes (e.g., methods returning `boolean`, arrays, numbers, objects as declared).

## Actual Behavior
- Methods are effectively `void` in emission/typing, causing `TS2322` and related errors when returning or using results.

## Impact
- Severity: High — Blocks compiling adapter TS using explicit FRM return types.

## Verification Tests
- Adapter FRM compile (framec → tsc) should pass with no `TS2322` once returns are honored.
- Minimal fixture under V3 capabilities: action declared `(): boolean` with native body and a `return true;` must compile cleanly to TS and type-check.

## Closure Requirements (shared env + adapter)
- **Compiler/toolchain version**
  - Use `framec v0.86.54` or later where V3 TS codegen reads action/operation header return types.
  - Ensure the shared env runtime d.ts is up to date (Bug #086 fixed).
- **Adapter FRM alignment**
  - Review `src/debug/state_machines/FrameDebugAdapter.frm` and:
    - Ensure any actions/operations that logically return a value (e.g. boolean, array) declare that type in their header (`foo(...): boolean`, `bar(...): SomeType[]`, etc.).
    - Ensure call sites and surrounding code expect the same type (no leftover `void`-style usage if the method now returns a value).
- **Compile + type-check**
  - With `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec`:
    - `OUT_DIR=$(mktemp -d)`
    - `$FRAMEC_BIN compile -l typescript -o "$OUT_DIR" src/debug/state_machines/FrameDebugAdapter.frm`
  - Use the same `tsconfig.json` pattern as Bug #084 to map `frame_runtime_ts` to the shared d.ts.
  - Run `tsc`:
    - `/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/node_modules/.bin/tsc -p "$OUT_DIR/tsconfig.json"`  
  - Requirement: `tsc` must not report `TS2322` (or similar) complaining that a value-returning action/operation is not assignable to `void`.
- **If errors remain**
  - Attach to this bug:
    - The relevant header(s) from `FrameDebugAdapter.frm`.
    - The corresponding generated TS signatures from `FrameDebugAdapter.ts` under `$OUT_DIR`.
    - The exact `tsc` error messages/line numbers.
  - This will allow us to distinguish between:
    - A remaining generator bug, vs.
    - An FRM-level type mismatch or stale call site.

## Next Steps (as agreed)
- Adapter team reruns the documented flow with the current framec:
  - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec`
  - `OUT_DIR=$(mktemp -d)`
  - `$FRAMEC_BIN compile -l typescript -o "$OUT_DIR" src/debug/state_machines/FrameDebugAdapter.frm`
  - `tsc -p "$OUT_DIR/tsconfig.json"` with the `frame_runtime_ts` mapping described above.
- If `tsc` still reports `TS2322` (or similar), attach to this bug:
  - The relevant headers from `FrameDebugAdapter.frm`.
  - The corresponding generated TS signatures from `FrameDebugAdapter.ts`.
  - The exact `tsc` errors and lines.
- With that data, compare FRM vs generated TS and either:
  - Adjust the V3 TS generator again if there’s a remaining compiler issue, or
  - Confirm it’s an FRM/call‑site mismatch and update this bug accordingly.

## Team Note (0.86.55 status + next steps)
- framec 0.86.55
  - Per release notes, includes V3 TS return‑type propagation and router arity fixes.
  - Binary used here: `/Users/marktruluck/projects/frame_transpiler/target/release/framec`.
- Internal validation already performed in the shared env
  - Shared adapter smoke: `ADAPTER_SMOKE_OK` on 0.86.55.
  - Adapter FRM compile via shared harness now passes (`TS_COMPILE_OK`) after FRM header corrections (details in Work Log).
- Action for adapter team (to confirm or narrow):
  - Rerun the documented harness on 0.86.55:
    - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec`
    - `OUT_DIR=$(mktemp -d)`
    - `$FRAMEC_BIN compile -l typescript -o "$OUT_DIR" src/debug/state_machines/FrameDebugAdapter.frm`
    - `tsc -p "$OUT_DIR/tsconfig.json"` (with the `frame_runtime_ts` mapping).
  - If clean: mark this bug `Fixed` and proceed to closure (84 remains Closed).
  - If not: attach the FRM headers for the affected actions/ops, the generated TS signatures, and exact `tsc` error lines so we can compare FRM vs emitted TS and determine whether further generator changes are needed.

## Evidence (0.86.55) — FRM vs generated TS

- Toolchain
  - framec: `/Users/marktruluck/projects/frame_transpiler/target/release/framec` → `framec 0.86.55`
  - TS compile harness: `adapter_protocol/scripts/ts_compile_fixture.sh`

- tsc errors
  - `TS2322: Type 'boolean' is not assignable to type 'void'.`
  - Reported at generated `FrameDebugAdapter.ts` lines: 1284, 1286, 1300 (from harness output)

- Generated TS around error sites (signatures and returns)
  ```ts
  // sendCommand — generated signature vs returns
  public sendCommand(commandType, data): void {
    if (this.debugServer) {
      frameRuntimeSendCommand(this.debugServer, commandType, data);
      this.sendDebugConsole(`Sent command: ${commandType}`);
      return true;   // <-- TS2322
    }
    return false;    // <-- TS2322
  }

  // testMessaging — generated signature vs return
  public testMessaging(): void {
    this.sendDebugConsole("Testing messaging protocol...");
    this.sendCommand("ping", {"timestamp": frameRuntimeGetTimestamp()});
    this.sendCommand("initialize", {"debugger": "Frame VS Code"});
    return true;     // <-- TS2322
  }
  ```

- Corresponding FRM headers (current)
  - src/debug/state_machines/FrameDebugAdapter.frm:749 — `sendCommand(commandType, data): void` (returns boolean in body)
  - src/debug/state_machines/FrameDebugAdapter.frm:759 — `testMessaging(): void` (returns boolean in body)
  - Note: other actions that return booleans are correctly declared and generated as `boolean`:
    - 517 `createTcpServer(): boolean`
    - 533 `spawnPythonMinimal(): boolean`
    - 549 `transpileFrameFile(): boolean`
    - 577 `spawnFramePython(): boolean`

- Interpretation
  - The current TS2322 failures are FRM-level header/body mismatches (declared `void`, returning `boolean`), not generator return-type propagation for these methods. Adjusting the FRM headers of `sendCommand` and `testMessaging` to `: boolean` should resolve these specific errors.

## Work Log
- 2025-11-21: Filed after 87 fix; remaining errors are `TS2322` void vs boolean for `spawnPython*`/`transpile*` paths — vscode_editor
- 2025-11-21: Revalidated on v0.86.54 — compile still fails with `TS2322` at OUT/FrameDebugAdapter.ts:1284, 1286, 1300 (boolean not assignable to void). Bug remains Open. — vscode_editor
- 2025-11-21: Implemented V3 TS codegen changes to honor action/operation header return types and validated against V3 capabilities fixtures and CLI tests. — framepiler team
 - 2025-11-21: Shared env harness: ts_compile_fixture failed for `FrameDebugAdapter.frm` with
   `TS2322` at lines 1284, 1286, 1300; shared smoke `ADAPTER_SMOKE_OK` unaffected. Command path:
   `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec adapter_protocol/scripts/ts_compile_fixture.sh src/debug/state_machines/FrameDebugAdapter.frm`. — vscode_editor
 - 2025-11-22: Revalidated on `framec 0.86.55` (claims return-type + router fixes). Result:
   `tsc` still reports `TS2322` at OUT/FrameDebugAdapter.ts:1284, 1286, 1300 when compiling the
   adapter FRM via shared harness; shared smoke remains `ADAPTER_SMOKE_OK`. Keeping status: Reopen. — vscode_editor
 - 2025-11-22: Updated FRM headers to match bodies: `sendCommand(commandType, data): boolean` and
   `testMessaging(): boolean`. Re-ran shared harness on `framec 0.86.55` → `TS_COMPILE_OK` for
   FrameDebugAdapter.frm. Conclusion: prior failures were FRM header/body mismatches, not a generator
   return‑type issue for these methods. Closing bug. — vscode_editor
