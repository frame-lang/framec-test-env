# Bug #082: V3 TypeScript — generated methods lose return value (drainCommands undefined)

## Metadata
bug_number: 082
title: V3 TypeScript — generated methods lose return value (drainCommands undefined)
status: Closed
priority: High
category: CodeGen
discovered_version: v0.86.51
fixed_version: v0.86.53
reporter: vscode_editor (Codex)
assignee: framepiler team
created_date: 2025-11-19
resolved_date: 2025-11-20

## Description
In the generated TS for a multi-state system, interface method variants that should return a value (e.g., drainCommands returning the result of flushCommands) sometimes evaluate to undefined at runtime. This manifests where cmds.some/cmds.filter throw because cmds is undefined (observed in adapter tests after start and before ready). Expect: drainCommands() returns an array consistently when FRM action returns flushCommands().

## Reproduction Steps
1) Ensure framec is v0.86.51.
2) Run shared env smoke:  
   `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec /Users/marktruluck/projects/framepiler_test_env/adapter_protocol/scripts/run_adapter_smoke.sh`.

## Repro Shortcuts (shared env)
- `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec /Users/marktruluck/projects/framepiler_test_env/adapter_protocol/scripts/run_adapter_smoke.sh`

## Work Log
- 2025-11-19: Filed with minimal FRM and validator — vscode_editor
 - 2025-11-19: Fixed in v0.86.53 by changing V3 TypeScript interface wrappers to return `any` and forward the return value of `_frame_router`, and by updating `_frame_router` to `return` the result of the underlying `_event_*` handler. This ensures methods like `drainCommands()` surface the array produced by `flushCommands()` rather than `undefined`. Validated via the v3_cli fixtures (`multi_state_interface_router`, `adapter_protocol_minimal`) and manual inspection of generated TS for a minimal FRM.
 - 2025-11-20: Verified OK on v0.86.54 using shared env smoke (ADAPTER_SMOKE_OK) — vscode_editor
