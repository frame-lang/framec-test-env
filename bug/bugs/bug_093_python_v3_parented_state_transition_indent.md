# Bug #093: Python V3 codegen mis-indents transitions with parented states (IndentationError)

## Metadata
```yaml
bug_number: 093
title: "Python V3 codegen mis-indents transitions with parented states (IndentationError)"
status: Closed
priority: High
category: CodeGen
discovered_version: v0.86.59
fixed_version: v0.86.59
reporter: Codex
assignee:
created_date: 2025-11-27
resolved_date: 2025-11-27
```

## Description
Adding a `$Default` parent state (to host a unified `ping()` handler) to `PythonDebugRuntime.fpy` causes the Python V3 codegen to emit mis-indented transition code in the generated `PythonDebugRuntime.py`. The resulting file fails `python3 -m py_compile` with `IndentationError: unexpected indent` around the generated `next_compartment = FrameCompartment(...)` lines.

## Reproduction Steps
1. `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec /Users/marktruluck/projects/frame_transpiler/target/release/framec compile -l python_3 -o /tmp/gen src/debug/state_machines/PythonDebugRuntime.fpy`
2. Open `/tmp/gen/PythonDebugRuntime.py` (or the workspace build `rebuild/PythonDebugRuntime.py`).
3. Observe mis-indented transition code, e.g.:
   ```
            if self.stopOnEntry:
                                    next_compartment = FrameCompartment("__PythonDebugRuntime_state_WaitingForEntry")
            self._frame_transition(next_compartment)
            return
   ```
4. Run `python3 -m py_compile /tmp/gen/PythonDebugRuntime.py` (or `python3 -m py_compile rebuild/PythonDebugRuntime.py`).
5. Python raises `IndentationError: unexpected indent` (line ~698 in the attached artifact).

## Expected Behavior
Generated Python should use valid indentation for transition expansions, even when states inherit from a parent (e.g., `$Default`). `py_compile` should succeed.

## Actual Behavior
The generated file contains over-indented `next_compartment = ...` lines inside handlers, producing `IndentationError` before runtime start.

## Impact
- Generated Python debug runtime cannot run with a parented `$Default` state; blocks adding shared handlers (e.g., `ping`) and prevents runtime smokes from executing.
- Affects Python V3 target when using parented states with transitions.

## Workaround
- Avoid parented states in the runtime FRM; keep manual transitions or inline helpers without inheritance. This is undesirable for shared handlers.

## Build/Release Artifacts
- framec binary: `/Users/marktruluck/projects/frame_transpiler/target/release/framec` (v0.86.59)
- Source FRM: `/Users/marktruluck/vscode_editor/src/debug/state_machines/PythonDebugRuntime.fpy`
- Generated artifact (failing): `/Users/marktruluck/vscode_editor/rebuild/PythonDebugRuntime.py`
- Shared artifact copy: `/Users/marktruluck/projects/framepiler_test_env/bug/artifacts/093/PythonDebugRuntime.py`

## Proposed Solution
- Fix Python V3 codegen to emit correctly indented transition blocks when states inherit from a parent (e.g., `$Default`). Ensure nested conditionals + parented states do not introduce extra leading spaces.
- Add a regression test that compiles a FRM with a parent state and transitions (like `PythonDebugRuntime.fpy` with `$Default`) and runs `python3 -m py_compile` on the generated Python.

## Test Coverage
- [ ] Unit test added
- [ ] Integration test added
- [x] Regression test added
- [x] Manual testing completed

## Work Log
- 2025-11-27: Introduced `$Default` parent with `ping()` in `PythonDebugRuntime.fpy`; generated Python fails `py_compile` with mis-indented `next_compartment` lines (see artifact). Filing as a codegen defect for parented-state transitions in Python V3.
- 2025-11-27: Updated Python V3 handler emission in `frame_transpiler` to use a normalized indentation helper for handler bodies. The helper preserves relative nesting, aligns Frame expansion lines (`next_compartment = FrameCompartment(...)`, `_frame_transition`, parent forwards) to the surrounding block, and respects colon-terminated lines so the first statement in a block is indented one level deeper.
- 2025-11-27: Validation with reference compiler `v0.86.59` (workspace binary copied to `bug/releases/frame_transpiler/v0.86.59`):
  - Rebuild debug runtime:  
    `FRAMEC_BIN=bug/releases/frame_transpiler/v0.86.59 bug/releases/frame_transpiler/v0.86.59 compile -l python_3 -o /tmp/gen_093 /Users/marktruluck/vscode_editor/src/debug/state_machines/PythonDebugRuntime.fpy`
  - Syntax check new output:  
    `python3 -m py_compile /tmp/gen_093/PythonDebugRuntime.py` (passes, no \`IndentationError\`).
  - Legacy shared artifact `bug/artifacts/093/PythonDebugRuntime.py` still reflects the old broken output and continues to fail `py_compile`; it is kept only as an archived repro artifact.
- 2025-11-27: Closure verification on framec 0.86.65 — rebuilt runtime with `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec` to `/tmp/gen_bug093` and `python3 -m py_compile /tmp/gen_bug093/PythonDebugRuntime.py` passed; marking Closed.
