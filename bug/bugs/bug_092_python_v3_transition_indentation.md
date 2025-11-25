# Bug #092: Python V3 codegen mis-indents transitions (IndentationError)

## Metadata
```yaml
bug_number: 092
title: "Python V3 codegen mis-indents transitions (IndentationError)"
status: Open
priority: High
category: CodeGen
discovered_version: v0.86.58
fixed_version:
reporter: Codex
assignee:
created_date: 2025-11-26
resolved_date:
```

## Description
When compiling the debugger runtime `src/debug/state_machines/PythonDebugRuntime.fpy` with V3 Python codegen, the generated `PythonDebugRuntime.py` contains over-indented `next_compartment = FrameCompartment(...)` lines inside handler branches. The result is an `IndentationError` at runtime (`unindent does not match any outer indentation level`), so the generated runtime cannot run.

## Reproduction Steps
1. `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec /Users/marktruluck/projects/frame_transpiler/target/release/framec compile -l python_3 -o /tmp/gen src/debug/state_machines/PythonDebugRuntime.fpy`
2. Open `/tmp/gen/PythonDebugRuntime.py` (or the workspace build at `rebuild/PythonDebugRuntime.py`).
3. Observe over-indented transition lines, e.g.:
   ```
            # Skip stop on entry if user continues
                            next_compartment = FrameCompartment("__PythonDebugRuntime_state_Running")
            self._frame_transition(next_compartment)
   ```
4. Run `python3 -m py_compile /tmp/gen/PythonDebugRuntime.py`.
5. Python raises `IndentationError: unindent does not match any outer indentation level` (around the lines above).

## Expected Behavior
Generated Python should use valid indentation for transition expansions (e.g., `next_compartment = ...` aligned with surrounding code) so the module passes `python3 -m py_compile` and can execute.

## Actual Behavior
Generated code includes mis-indented transition lines inside handlers, causing `IndentationError` before runtime start.

## Impact
- Generated Python debug runtime cannot execute; blocks adapter↔runtime end-to-end validation.
- Affects V3 Python target when emitting transitions inside nested conditionals.

## Workaround
- None clean. Avoiding `->` and hand-inlining transitions is not acceptable; codegen must emit valid Python.

## Build/Release Artifacts
- framec binary: `/Users/marktruluck/projects/frame_transpiler/target/release/framec` (v0.86.58)
- Source FRM: `/Users/marktruluck/vscode_editor/src/debug/state_machines/PythonDebugRuntime.fpy`
- Generated artifact (failing): `/Users/marktruluck/vscode_editor/rebuild/PythonDebugRuntime.py`
- Shared artifact copy: `/Users/marktruluck/projects/framepiler_test_env/bug/artifacts/092/PythonDebugRuntime.py`

## Proposed Solution
- Fix Python V3 codegen so `-> $State` expansions emit correctly indented `next_compartment` blocks inside nested conditionals/handlers. Ensure no over-indentation relative to the active block.
- Add a regression test that compiles a FRM with conditional transitions (e.g., the debugger runtime) and runs `python3 -m py_compile` to catch indentation errors.

## Test Coverage
- [ ] Unit test added
- [ ] Integration test added
- [ ] Regression test added
- [ ] Manual testing completed

## Work Log
- 2025-11-26: Discovered during runtime smoke attempts; generated `PythonDebugRuntime.py` fails `py_compile` due to over-indented transition lines. Artifact saved to `bug/artifacts/092/PythonDebugRuntime.py`.
