# Bug #074: TypeScript generator omits actions/domain declarations and drops interface params

## Metadata
bug_number: 074
title: TypeScript generator omits actions/domain declarations and drops interface params
status: Closed
priority: High
category: CodeGen
discovered_version: v0.86.42
fixed_version: v0.86.49
reporter: vscode_editor (Codex)
assignee: framepiler team
created_date: 2025-11-15
resolved_date: 2025-11-20

## Reopen Reason
Regression observed with framec v0.86.48 via minimal module validator (#078 context). `tsc` reports constructor arity errors and missing fields when compiling minimal generated TS module against runtime types.

## How to Validate (shared env)
- Run shared env smoke:  
  `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec /Users/marktruluck/projects/framepiler_test_env/adapter_protocol/scripts/run_adapter_smoke.sh`
- Expected: `ADAPTER_SMOKE_OK` on versions ≥ v0.86.49 (confirmed on v0.86.54)
- Note: Legacy `/tmp` validators are deprecated and not used.

## Work Log
- 2025-11-18: Reopened — validators fail on v0.86.48 (see Bug #078) — vscode_editor
- 2025-11-18: Marked Fixed in v0.86.49 — runtime d.ts aligned with generator (see Bug #078); v3_cli TS tests (`actions_and_domain_emit_issues`) green and minimal module validators expected to type-check.
- 2025-11-20: Verified in shared env on v0.86.54 (`run_adapter_smoke.sh`); closed — vscode_editor
