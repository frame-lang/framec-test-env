# Bug #087: TypeScript codegen mis-parses `if`/`for` into invalid method headers

## Metadata
bug_number: 087
title: TypeScript codegen mis-parses `if`/`for` into invalid method headers
status: Closed
priority: High
category: CodeGen
discovered_version: v0.86.54
fixed_version: v0.86.54
reporter: vscode_editor (Codex)
assignee: framepiler team
created_date: 2025-11-20
resolved_date: 2025-11-21

## Description
When compiling a V3 system with `@target typescript` and TS-native action bodies, the generator emits broken code where `if (...) { ... }` and `for (...) { ... }` statements are transformed into top-level method declarations like:

```
public if(result.success): void {
  ...
}
public for(const sourceFrame of frameRuntimeMapKeys(this.frameSourceMap): void {
  ...
}
```

These are invalid TypeScript and cause numerous `TS1005`/`TS1128`/`TS1109` errors. This appears after adding explicit return types in action headers (e.g., `spawnFramePython(): boolean { ... }`), suggesting the TS codegen’s body emission/splitting is incorrectly treating native control-flow keywords as method headers.

## Reproduction Steps
1) Generate TS from the adapter FRM (this repo’s copy reflects TS-native bodies and return types):
   - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec`
   - `OUT_DIR=rebuild/gen_bug087`
   - `$FRAMEC_BIN compile -l typescript -o $OUT_DIR src/debug/state_machines/FrameDebugAdapter.frm`
2) Inspect `$OUT_DIR/FrameDebugAdapter.ts` around the indicated regions. Example excerpts:
   - Near 1000–1080:
     ```ts
     public if(result.success): void {
       this.pythonProcess = result.process;
       this.sendDebugConsole(`Python process spawned: PID ${result.pid}`);
       return true;
     }
     public if(!(transpileResult.success): void {
       this.sendDebugConsole(`Transpilation failed: ${transpileResult.error}`);
       return false;
     }
     public for(const sourceFrame of frameRuntimeMapKeys(this.frameSourceMap): void {
       // ...
     }
     ```
   - Near ~740–770, object literal sections are correct after normalization, so the critical issue is the `if`/`for` emission becoming method headers.
3) Compile with shared env d.ts mapping:
   - Create `tsconfig.json` in OUT that maps `frame_runtime_ts` to the shared d.ts.
   - Run tsc: `/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/node_modules/.bin/tsc -p $OUT_DIR/tsconfig.json`
4) Observe `TS1005`, `TS1128`, `TS1109` errors at the lines shown above.

Alternative minimal repro (V3 capabilities fixture in main repo):
5) In the Frame Transpiler repo, compile:
   - `FRAMEC_BIN=./target/release/framec`
   - `OUT_DIR=/tmp/bug087_out`
   - `$FRAMEC_BIN compile -l typescript -o $OUT_DIR framec_tests/language_specific/typescript/v3_capabilities/type_and_default/positive/if_for_actions_return_type_v3.frm`
6) Inspect `$OUT_DIR/if_for_actions_return_type_v3.ts` and confirm that no methods named `if`/`for` are emitted (post-fix).

## Build/Release Artifacts
- framec binary used for repro and fix validation:
  - `../frame_transpiler/target/release/framec`
- Adapter FRM compile output (debugger repo / shared env workflow):
  - `rebuild/gen_bug087/FrameDebugAdapter.ts`
- Minimal V3 capabilities fixture (main repo):
  - Source: `../frame_transpiler/framec_tests/language_specific/typescript/v3_capabilities/type_and_default/positive/if_for_actions_return_type_v3.frm`
  - Generated TS (local validation): `/tmp/bug087_out/if_for_actions_return_type_v3.ts`

## Expected Behavior
- Native `if (...) { ... }` and `for (...) { ... }` inside action/operation bodies remain statements within the generated method body; they must not become top-level method signatures.

## Actual Behavior
- Generator emits invalid method headers like `public if(...): void {` and `public for(...): void {` where control-flow statements should be.

## Impact
- Severity: High — Generated TS does not compile, blocking adapter integration.
- Scope: Any TS target with annotated return types and native control-flow inside actions/operations.

## Technical Analysis (initial)
- Likely interaction between the action header return-type parsing and the body emission pipeline that splits by SOL tokens; the native scanner or emitter may be mistakenly interpreting `if`/`for` lines as headers.
- Check TS emitter responsible for method header vs. body emission and ensure SOL-based splitting does not reclassify native statements.

## Proposed Solutions
- Ensure the TS body emitter treats `if`, `for`, `while`, etc., as native statements within the method body, not headers.
- Prefer structured emission (AST or templated statement blocks) over string-splice that can confuse separators and keywords.
- Add regression tests using a minimal fixture with annotated returns and native `if`/`for` in actions.

## Verification Tests
- Minimal V3 fixture in main repo:
  - `framec_tests/language_specific/typescript/v3_capabilities/type_and_default/positive/if_for_actions_return_type_v3.frm`
  - Exercised via:
    - `python3 framec_tests/runner/frame_test_runner.py --languages python typescript --categories all_v3 --framec ./target/release/framec --transpile-only`
  - Generated TS must not contain `public if(` or `public for(`, and the action header
    `spawnFramePython(): boolean { ... }` must compile into a single method body.
- Adapter shared-env smoke (regression guard at protocol level):
  - `FRAMEC_BIN=../frame_transpiler/target/release/framec ./adapter_protocol/scripts/run_adapter_smoke.sh`
  - Expected: `ADAPTER_SMOKE_OK`.

## Work Log
- 2025-11-20: Filed with excerpts from generated `FrameDebugAdapter.ts` showing `public if(...): void` and `public for(...): void` — vscode_editor
- 2025-11-21: Root cause identified — `OutlineScannerV3::scan` did not recognize typed section headers
  like `spawnFramePython(): boolean { ... }`, so those lines were treated as plain statements and inner
  `if` / `for` lines were misclassified as new `Action` bodies. — framepiler team
- 2025-11-21: Implemented fix in `framec/src/frame_c/v3/outline_scanner.rs`:
  - Extended header detection for section members (machine/actions/operations/interface) to allow
    optional `: Type = default` segments between `)` and `{`.
  - Added a control-flow keyword guard so `if` / `for` / `while` / `switch` are never interpreted as
    section-member names even when followed by `(...) { ... }`.
  - Added minimal fixture `if_for_actions_return_type_v3.frm` to V3 TS capabilities to lock in behavior.
  - Rebuilt `framec` and re-ran the full V3 TS/Python transpile-only suite and the shared adapter
    smoke test; all passed.
- 2025-11-21: Marked status `Fixed` in this shared-env tracker for version `v0.86.54`; awaiting debugger
  team closure after revalidating their full `FrameDebugAdapter.frm` scenario. — framepiler team
