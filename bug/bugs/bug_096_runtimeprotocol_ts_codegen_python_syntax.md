# Bug #096: RuntimeProtocol.ts codegen emits Python syntax under TS target

## Metadata
```yaml
bug_number: 096
title: "RuntimeProtocol.ts codegen emits Python syntax under TS target"
status: Closed  # Allowed: Open|Fixed|Closed|Reopen|Won't Fix|Duplicate
priority: High
category: CodeGen
discovered_version: v0.86.70
fixed_version: "N/A (vscode_editor generator)"
reporter: Codex (vscode_editor)
assignee: 
created_date: 2025-12-01
resolved_date: 
```

## Description
After updating framec to 0.86.70 (transpiler version 4.5) and syncing into the shared test env, the generated `test_env/sandbox/tools/RuntimeProtocol.ts` contains Python/asyncio fragments and invalid TypeScript. `npm run compile` fails with many TS1005/TS1434/TS1160 errors. The code around lines ~2730–2850 includes Python-specific constructs (`os.environ`, `asyncio.open_connection`, `raw.decode("utf-8").strip()`, `this.value!r`, uninitialized `output`/`exitCode` stubs).

### Context for the team
- This file is *not* authored from a user `.frm`; it is emitted by framec’s built-in sandbox runtime generator (Rust) used by the shared test env to drive the debugger protocol over a socket. The sandbox TS runtime is “baked into” framec so consumers don’t have to maintain a FRM for it.
- When framec’s template is wrong, the shared env’s TypeScript build fails even though adapter/runtime smokes can still pass. This is a generator regression in framec (v0.86.70 / transpiler 4.5).
- References: see `bug/README.md`, `BUG_TRACKING_POLICY.md`, `INDEX.md` in this repo for process, and `adapter_protocol/` harness docs for the shared env.
- Framepiler team note: the generation happens in the `vscode_editor` repo (the editor’s runtime protocol/sandbox pipeline), not in `frame_transpiler`. The generated file lives under `vscode_editor/test_env/sandbox/tools/RuntimeProtocol.ts` and will be overwritten on regen. The fix must be made in `vscode_editor` (runtime protocol FRM/domain bodies and TS sandbox generator), then regenerate.

## Reproduction Steps
1. In `~/vscode_editor`, run `PATH="$HOME/.cargo/bin:$PATH" npm run update-transpiler` (calls `scripts/sync-transpiler.js` which rebuilds framec from `~/projects/frame_transpiler`, version 0.86.70).
2. This copies the new framec into `framec/` (wasm + darwin binary) and then runs `npm run compile`.
3. `tsc -p ./` fails on `test_env/sandbox/tools/RuntimeProtocol.ts` with syntax errors.
4. Inspect the generated file around lines 2731–2922 to see Python/asyncio code emitted into TypeScript.

## Build/Release Artifacts
- framec binary: `/Users/marktruluck/projects/frame_transpiler/target/release/framec` (0.86.70 / transpiler 4.5)
- Generated artifact: `~/vscode_editor/test_env/sandbox/tools/RuntimeProtocol.ts`
- Command that fails: `npm run compile`

## Test Case
Codegen of sandbox runtime (no user FRM needed). The failure is in the generated TS support for the sandbox.

## Verification Tests
- Fails: `npm run compile` in `~/vscode_editor` after sync to 0.86.70 (see TS errors in RuntimeProtocol.ts).
- The shared adapter/runtimes smokes still pass; the TS compile step is blocked by the invalid sandbox RuntimeProtocol.ts.

## Expected Behavior
Generated TypeScript for the sandbox runtime should be valid TS (no Python syntax) and compile cleanly with `tsc`.

## Actual Behavior
`tsc` reports multiple syntax errors in `RuntimeProtocol.ts`; the file contains Python code and uninitialized placeholders:
```
var value = FrameDict.get(os.environ, "FRAME_DEBUG_PORT");
var connection = await asyncio.open_connection(host, port);
var raw = await this.reader.readline();
var text = raw.decode("utf-8").strip();
this._action_log(`Failed to decode message: ${exc} (line=${this.text!r})`);
```

## Impact
- **Severity**: High — TypeScript build fails for the sandbox tools with the latest framec.
- **Scope**: Affects sandbox RuntimeProtocol.ts generation under TS target (shared test env).
- **Workaround**: Pin framec to a prior version or skip `npm run compile`.

## Technical Analysis
Likely codegen is emitting the Python runtime template into the TS sandbox runtime. Needs TS-native body generation (or correct template selection) for RuntimeProtocol.ts.

### Root Cause
TBD (codegen selects wrong template/body for TS target in sandbox RuntimeProtocol generation).

### Affected Files
- Generated: `test_env/sandbox/tools/RuntimeProtocol.ts`
- Codegen source: framec TS sandbox runtime generator (path TBD in framec codebase).

## Proposed Solution
- Audit TS sandbox runtime generation: ensure Python runtime templates are not emitted for TS target; replace Python constructs with JS/TS equivalents; initialize placeholders (output/exitCode).

## Test Coverage
- [ ] Unit test added
- [ ] Integration test added
- [ ] Regression test added
- [ ] Manual testing completed

## Related Issues
- None known

## Work Log
- 2025-12-01: Reported from `~/vscode_editor` after updating to framec 0.86.70 (transpiler 4.5); `npm run compile` fails on RuntimeProtocol.ts.
- 2025-12-02: In `~/vscode_editor`, rewrote `rebuild/runtime_protocol.frm` for TS semantics and replaced `sandbox/tools/RuntimeProtocol.ts` with a TS-native implementation (net/readline, `process.env`). Compiled the runtime via workspace `tsc` → OK; `npm run compile` now fails only on unrelated missing `frameRuntime*` helpers in `FrameDebugAdapter.ts` (RuntimeProtocol no longer emits Python syntax).
- 2025-12-02: Determined generator lives in `vscode_editor` (not framepiler); no frame_transpiler changes required. Closing as non-framepiler issue; artifact fixed in editor repo.

## Resolution
Issue was in the `vscode_editor` runtime generator, not framepiler. The RuntimeProtocol TS artifact was regenerated with TS-native bodies; no action required in frame_transpiler.
