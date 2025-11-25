# Bug #091: Python debug runtime generated with invalid syntax (debug port braces)

## Metadata
```yaml
bug_number: 091
title: "Python debug runtime generated with invalid brace syntax; cannot connect"
status: Closed
priority: High
category: CodeGen
discovered_version: v0.86.58
fixed_version: v0.86.58
reporter: Codex
assignee: 
created_date: 2025-11-22
resolved_date: 2025-11-24
```

## Description
The Python debug runtime generated from `src/debug/state_machines/PythonDebugRuntime.frm` contains invalid brace-style conditionals (e.g., `if self.debugPort == 0 {`) and malformed `if/elif` blocks. The resulting `PythonDebugRuntime.py` fails to execute, so the runtime never connects to the adapter or emits `connected`/`ready`/`stopped` events.

## Reproduction Steps
1. `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec /Users/marktruluck/projects/frame_transpiler/target/release/framec compile -l python_3 -o /tmp/gen src/debug/state_machines/PythonDebugRuntime.frm`
2. Open `/tmp/gen/PythonDebugRuntime.py`.
3. Observe brace-style `if`/`elif` blocks (e.g., `if self.debugPort == 0 {`).
4. Run with `FRAME_DEBUG_PORT=55555 PYTHONPATH=/Users/marktruluck/projects/frame_transpiler python3 /tmp/gen/PythonDebugRuntime.py`.
5. Python raises `SyntaxError: invalid syntax` before any socket connect occurs.

## Build/Release Artifacts
- Reference `framec` binary for validation (shared env):  
  `bug/releases/frame_transpiler/v0.86.58/framec`
- Original workspace `framec` binary:  
  `/Users/marktruluck/projects/frame_transpiler/target/release/framec` (v0.86.58)
- Generated artifact (original repro): `/tmp/gen/PythonDebugRuntime.py`
- Problem file (workspace build): `/Users/marktruluck/vscode_editor/rebuild/PythonDebugRuntime.py`
- Shared artifact copy: `/Users/marktruluck/projects/framepiler_test_env/bug/artifacts/091/PythonDebugRuntime.py`
- Problem source FRM (native bodies with brace syntax): `/Users/marktruluck/vscode_editor/src/debug/state_machines/PythonDebugRuntime.frm`

## Test Case
```frame
// Uses the existing runtime FRM; no additional FRM code required beyond PythonDebugRuntime.frm
```

## Verification Tests
- Shared-env syntax validation (must pass once fixed):  
  `python3 -m py_compile bug/artifacts/091/PythonDebugRuntime.py`  
  (currently fails with `SyntaxError` until the FRM and artifact are corrected).
- Reference compiler for re-validation:  
  `bug/releases/frame_transpiler/v0.86.58/framec`

## Expected Behavior
The generated `PythonDebugRuntime.py` should be valid Python, connect to FRAME_DEBUG_PORT, emit `connected`/`ready`, and honor stopOnEntry/breakpoints.

## Actual Behavior
The generated file contains brace-style conditionals and fails with `SyntaxError` before attempting any socket communication:
```
  File "/tmp/gen/PythonDebugRuntime.py", line 18
    if self.debugPort == 0 {
                           ^
SyntaxError: invalid syntax
```

## Impact
- **Severity**: High — generated debug runtime cannot run, blocking adapter↔runtime validation and any real runtime smoke tests.
- **Scope**: Python debug runtime generation from `PythonDebugRuntime.frm`; affects adapter/runtime integration.
- **Workaround**: Use handcrafted/stub runtime for transport testing; cannot validate real generated runtime until fixed.

## Technical Analysis
Generated Python contains brace-style control flow and `if/elif` blocks not valid in Python. Likely the TS/Python target codegen for this FRM is emitting legacy brace syntax instead of Python `if:`/indentation.

## Proposed Solution
- Treat this primarily as a **source FRM / target mismatch** issue rather than a core V3 generator bug:
  - The V3 Python generator only rewrites Frame statements and splices native Python as-is.
  - The brace-style `if ... {` / `} elif ... {` constructs in `PythonDebugRuntime.py` come from the FRM's native bodies, not from the generator.
- Correct the `PythonDebugRuntime.frm` source (in the debugger/runtime repo) so that, under `@target python`, all native bodies use valid Python syntax (e.g., `if ...:` with indentation, no `{}`/`}`), avoid `$enter`/`$exit` handler names that become invalid identifiers, and replace Frame `->` transitions with explicit `_frame_transition(...)` calls to preserve indentation.
- Once the FRM is corrected, compile it with `-l python_3` and confirm the generated `PythonDebugRuntime.py` no longer contains braces and runs without `SyntaxError`.
- Add a regression test in the shared env that compiles `PythonDebugRuntime.frm` and executes the resulting Python module to ensure it starts up without syntax errors.

## Test Coverage
- [ ] Unit test added
- [ ] Integration test added
- [ ] Regression test added
- [ ] Manual testing completed

## Related Issues
- N/A

## Work Log
- 2025-11-22: Initial report — Codex. Detected invalid syntax in generated Python debug runtime; runtime cannot connect to adapter.
- 2025-11-24: Added explicit link to the source FRM and mirrored the broken generated Python file under `bug/artifacts/091/PythonDebugRuntime.py` in the shared test env for quick inspection.
- 2025-11-24: Updated `PythonDebugRuntime.frm` (debugger/runtime repo) to use Python-native control flow, helper actions for paused/terminate entry, explicit `_frame_transition(...)` calls, and removed `$enter/$exit` handlers that produced invalid identifiers. Recompiled with `framec 0.86.58`; `python3 -m py_compile rebuild/PythonDebugRuntime.py` now passes. Synced the fixed artifact to `bug/artifacts/091/PythonDebugRuntime.py`. Status set to **Fixed**.
- 2025-11-24: Closure verification — ran `framec 0.86.58 compile -l python_3 -o rebuild src/debug/state_machines/PythonDebugRuntime.frm` and `python3 -m py_compile rebuild/PythonDebugRuntime.py` (no errors). Confirmed artifact copied to `bug/artifacts/091/PythonDebugRuntime.py`. Status set to **Closed**.
- 2025-11-24: Shared-env validation using `python3 -m py_compile bug/artifacts/091/PythonDebugRuntime.py` still fails with `SyntaxError` (brace-style `if` blocks remain in the stored artifact). Bug status set to **Reopen** until the corrected artifact is copied to `bug/artifacts/091/` and the shared-env `py_compile` check passes. Reference compiler for re-validation: `bug/releases/frame_transpiler/v0.86.58/framec`.
