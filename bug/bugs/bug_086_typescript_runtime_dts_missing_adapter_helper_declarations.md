# Bug #086: TypeScript runtime d.ts missing adapter helper declarations

## Metadata
bug_number: 086
title: TypeScript runtime d.ts missing adapter helper declarations
status: Closed
priority: High
category: Runtime
discovered_version: v0.86.54
reporter: vscode_editor (Codex)
assignee: framepiler team
created_date: 2025-11-20
resolved_date: 2025-11-20
fixed_version: v0.86.54

## Description
The shared `frame_runtime_ts.d.ts` used for compiling generated TypeScript declares only `FrameEvent` and `FrameCompartment`. Adapter FRMs (e.g., FrameDebugAdapter) call a set of runtime helper functions (e.g., `frameRuntimeSetDebugAdapter`, `frameRuntimeCreateServer`, `frameRuntimeTranspileFrame`, `frameRuntimeInjectFrameDebugRuntime`, `frameRuntimeSpawnPython`, map APIs, etc.). These functions are not declared in the d.ts, causing `tsc` name resolution errors when compiling generated adapter modules.

## Reproduction Steps
1) Generate TS from `src/debug/state_machines/FrameDebugAdapter.frm` (adapter repo) using framec v0.86.54.
2) Compile with shared env `frame_runtime_ts.d.ts` in path-mapped `tsconfig.json`.
3) Observe `tsc` errors: unknown identifiers such as `frameRuntimeWait`, `frameRuntimeSetDebugAdapter`, `frameRuntimeCreateServer`, `frameRuntimeSetEnv`, `frameRuntimeSpawnPython`, `frameRuntimeTranspileFrame`, `frameRuntimeGetLength`, `frameRuntimeGetMapSize`, `frameRuntimeInjectFrameDebugRuntime`, `frameRuntimeMap*`, `frameRuntimeSendCommand/Response/Event`, etc.

## Expected Behavior
- The TS runtime types should include declarations for the adapter-facing helper functions used by V3 systems that integrate with the adapter runtime.

## Actual Behavior
- Only core types are declared; no function declarations exist for adapter/runtime helpers, breaking `tsc` for generated adapter modules.

## Impact
- Severity: High — blocks compiling generated adapter TS that references runtime helpers.
- Scope: Any adapter FRM or V3 TS module that interacts with the adapter runtime layer.

## Proposed Solutions
- Option A: Extend `frame_runtime_ts.d.ts` to declare the adapter helper API surface, e.g.:
  ```ts
  export declare function frameRuntimeSetDebugAdapter(ad: any): void;
  export declare function frameRuntimeCreateServer(): { port: number; server: any };
  export declare function frameRuntimeSetEnv(key: string, value: string): void;
  export declare function frameRuntimeSpawnPython(code: string): { success: boolean; process?: any; pid?: number; error?: string };
  export declare function frameRuntimeTranspileFrame(path: string, target: string, debug: boolean): { success: boolean; code: string; sourceMap: any; error?: string };
  export declare function frameRuntimeInjectFrameDebugRuntime(code: string, map: any, port: number): string;
  export declare function frameRuntimeWait(ms: number): void;
  export declare function frameRuntimeGetTimestamp(): number;
  // Map/collection helpers
  export declare function frameRuntimeMapGet(map: any, key: string): any;
  export declare function frameRuntimeMapSet(map: any, key: string, value: any): void;
  export declare function frameRuntimeMapHasKey(map: any, key: string): boolean;
  export declare function frameRuntimeMapKeys(map: any): string[];
  export declare function frameRuntimeGetLength(x: any): number;
  export declare function frameRuntimeGetMapSize(x: any): number;
  export declare function frameRuntimeToString(x: any): string;
  // Transport helpers
  export declare function frameRuntimeSendCommand(server: any, commandType: string, data: any): void;
  export declare function frameRuntimeSendResponse(command: string, body: any): void;
  export declare function frameRuntimeSendEvent(event: string, body: any): void;
  // Process/server lifecycle
  export declare function frameRuntimeCloseServer(server: any): void;
  export declare function frameRuntimeKillProcess(proc: any): void;
  ```
- Option B: Provide a separate `frame_adapter_runtime_ts.d.ts` consumed by adapter targets and referenced by path mapping alongside `frame_runtime_ts.d.ts`.

## Verification Tests
- Add a compile-only shared test with a minimal fixture that calls helper APIs:
  - Fixture: `adapter_protocol/test_fixture_ts_runtime_helpers.frm`
  - Command: `cd adapter_protocol && ./scripts/ts_compile_fixture.sh ./test_fixture_ts_runtime_helpers.frm`
  - Expected (before fix): `TS_COMPILE_FAIL` due to unknown identifiers (missing declarations in d.ts).
  - PASS (after fix): `TS_COMPILE_OK` when the extended d.ts is provided via path mapping and symbols resolve.

## Work Log
- 2025-11-20: Filed alongside Bug #085 while converting FRM bodies to TS; compile shows missing global helper declarations — vscode_editor
- 2025-11-20: Reproduced compile errors with `framec 0.86.54` + shared d.ts path-map. Errors include unknown identifiers (`frameRuntimeGetTimestamp`, `frameRuntimeWait`, `frameRuntimeFileExists`, `frameRuntimeMap*`, `frameRuntimeSend*`, etc.) and type errors stemming from unknown return types. Added minimal fixture and compile harness; will PASS once d.ts is extended per Proposed Solutions. — vscode_editor

## Framepiler Team TODO
- Extend runtime typings for adapter integration (preferred in `frame_runtime_ts.d.ts`, or provide a companion `frame_adapter_runtime_ts.d.ts`) to declare the helper APIs used by adapter FRMs:
  - `frameRuntimeGetTimestamp`, `frameRuntimeWait`
  - `frameRuntimeSetDebugAdapter`, `frameRuntimeCreateServer`, `frameRuntimeCloseServer`
  - `frameRuntimeSetEnv`, `frameRuntimeSpawnPython`, `frameRuntimeKillProcess`
  - `frameRuntimeTranspileFrame`, `frameRuntimeInjectFrameDebugRuntime`
  - Map helpers: `frameRuntimeMapGet/Set/HasKey/Keys`, and utilities: `frameRuntimeGetLength/GetMapSize/ToString`
  - Transport: `frameRuntimeSendCommand/Response/Event`
- Ensure declarations match the actual runtime surface (Node/JS).
- Re-run and validate:
  - Minimal fixture: `cd adapter_protocol && ./scripts/ts_compile_fixture.sh ./test_fixture_ts_runtime_helpers.frm` → expect `TS_COMPILE_OK`.
  - Full FDA: regenerate (framec), then `tsc` with shared tsconfig/path mapping → expect `TS_COMPILE_OK`.
  - Shared smoke: `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec /Users/marktruluck/projects/framepiler_test_env/adapter_protocol/scripts/run_adapter_smoke.sh` → expect `ADAPTER_SMOKE_OK`.

- 2025-11-20: Extended `adapter_protocol/runtime/frame_runtime_ts.d.ts` with declarations for adapter helper APIs (timers, env, map helpers, transport, process/server lifecycle). Re-ran fixture compile (`ts_compile_fixture.sh`) and shared smoke (`run_adapter_smoke.sh`) with `framec 0.86.54`; both PASS (`TS_COMPILE_OK`, `ADAPTER_SMOKE_OK`). Marking this bug Fixed for the shared env; full FDA compile remains tracked under Bug #084. — framepiler team
