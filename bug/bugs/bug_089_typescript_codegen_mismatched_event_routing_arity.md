# Bug #089: TypeScript codegen emits mismatched argument arity in _event_ routing

## Metadata
bug_number: 089
title: TypeScript codegen emits mismatched argument arity in _event_ routing
status: Closed
priority: High
category: CodeGen
discovered_version: v0.86.54
fixed_version: v0.86.54
reporter: vscode_editor (Codex)
assignee: framepiler team
created_date: 2025-11-21
resolved_date: 2025-11-21

## Description
Earlier, `_frame_router` calls to `_event_*` were generated with incorrect argument counts, leading to `TS2554` in adapter builds.

## Reproduction / Validation
- Regenerate adapter TS and compile with the shared d.ts mapping:
  - `framec -l typescript` → OUT (FrameDebugAdapter.ts)
  - `tsc -p OUT/tsconfig.json`
- On v0.86.54, no `TS2554` arity errors are observed in the current output; remaining failures are unrelated return-type issues tracked in Bug #088.

## Expected Behavior
- `_frame_router` and `_event_*` signatures align and compile without arity errors.

## Actual Behavior (historical)
- Prior to the fix, `_frame_router` and `_event_*` diverged and caused `TS2554`.

## Work Log
- 2025-11-21: Validated on v0.86.54 — arity `TS2554` no longer present. Closing. — vscode_editor

