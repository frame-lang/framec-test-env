# Bug #090: Python V3 nested `def` indentation error in scoping fixture

## Metadata
bug_number: 090
title: Python V3 nested `def` indentation error in scoping fixture
status: Closed
priority: Medium
category: CodeGen
discovered_version: v0.86.55
fixed_version: v0.86.55
reporter: frame_transpiler assistant
assignee:
created_date: 2025-11-22
resolved_date: 2025-11-22

## Description
When compiling the Python V3 scoping fixture `function_scope.frm`, the V3 Python
generator emits invalid Python code for a nested `def` immediately followed by a
Frame statement (`=> $^`) and additional native code. The body of the nested
function is not indented, so the generated file is syntactically invalid.

Fixture:

```frame
@target python

system S {
    machine:
        $A => $P {
            e() {
                def f():
                    return 1
                => $^
                f()
            }
        }
        $P { }
}
```

Generated Python around the error (excerpt from
`framec_tests/generated/python/function_scope.py`):

```python
def _event_e(self, __e: FrameEvent, compartment: FrameCompartment):
    c = compartment or self._compartment
    if c.state == "__S_state_A":

        def f():
        self._system_return_stack[-1] = 1
        return
        self._frame_router(__e, compartment.parent_compartment)

        f()
```

The nested `def f():` body is not indented, and the lines that follow align with
the `def` line instead of being part of its body. This is a code generation
error in the V3 Python emitter (MIR → PyExpanderV3 → splice), not a fixture
syntax error.

## Reproduction Steps
1) In the `frame_transpiler` repo with `framec v0.86.55` built:
   - `cd /Users/marktruluck/projects/frame_transpiler`
2) Run the curated V3 exec suite for Python/TypeScript core/control_flow/scoping/systems:
   ```bash
   python3 framec_tests/runner/frame_test_runner.py \
     --languages python typescript \
     --categories v3_core v3_control_flow v3_scoping v3_systems \
     --framec ./target/release/framec \
     --run --exec-v3
   ```
3) Observe that when `# @exec-ok` is present on
   `framec_tests/language_specific/python/v3_scoping/positive/function_scope.frm`,
   the test now passes and the generated Python has valid indentation as
   described in the Expected Behavior section.
4) Inspect the generated Python directly:
   ```bash
   sed -n '1,200p' framec_tests/generated/python/function_scope.py
   ```

## Build/Release Artifacts
- framec binary used:
  - `/Users/marktruluck/projects/frame_transpiler/target/release/framec` (v0.86.55)
- Fixture:
  - `../frame_transpiler/framec_tests/language_specific/python/v3_scoping/positive/function_scope.frm`
- Generated Python:
  - `../frame_transpiler/framec_tests/generated/python/function_scope.py`

## Expected Behavior
- The nested `def f():` should be emitted with a correctly indented body, and
  Frame statements plus native code around it should preserve valid Python
  indentation and semantics. For example, one acceptable expansion shape would
  be:

  ```python
  def _event_e(...):
      if c.state == "__S_state_A":
          def f():
              # body expands here
              self._system_return_stack[-1] = 1
              return
          self._frame_router(__e, compartment.parent_compartment)
          f()
  ```

  (Exact layout may vary, but the nested `def` body must be syntactically valid.)

## Actual Behavior (after fix)
- The nested `def f():` body is emitted with a properly indented body, and
  the Frame-generated router call is placed at the top level of the state
  guard. Python V3 scoping exec fixtures now run successfully under the
  curated exec suite.

## Work Log
- 2025-11-22 (v0.86.55) — Fix implemented
  - Updated the Python V3 handler emitter in `framec/src/frame_c/v3/mod.rs` to:
    - Normalize handler body indentation while preserving relative nesting
      for nested defs / blocks (both state-less and state-qualified handlers).
    - Rewrite `system.return` to the per-call stack slot
      `self._system_return_stack[-1]` inside handlers.
    - Apply handler-only sugar `return expr` → `system.return = expr; return`.
    - Treat `self._frame_router(__e, ...)` calls generated from Frame
      forward/transition semantics as top-level statements within the state
      guard so they are not accidentally nested under local defs/blocks.
  - Rebuilt `framec` with:
    - `cargo build --release -p framec`
  - Re-ran curated exec for V3 Py/TS core/control_flow/scoping/systems:
    - `python3 framec_tests/runner/frame_test_runner.py \
         --languages python typescript \
         --categories v3_core v3_control_flow v3_scoping v3_systems \
         --framec ./target/release/framec \
         --run --exec-v3`
    - Result: Python 68/68, TypeScript 72/72 exec passing; Python
      `v3_scoping` fixtures (`function_scope`, `nested_functions`,
      `shadowing`) all run successfully.
- 2025-11-22 (v0.86.56) — Fix verified and bug closed
  - Bumped the Frame Transpiler version to `0.86.56` and rebuilt release
    artifacts:
    - `cargo build --release` (workspace version `0.86.56`)
  - Re-validated V3 transpile-only suites for Python/TypeScript:
    - `python3 framec_tests/runner/frame_test_runner.py \
         --languages python typescript \
         --categories all_v3 \
         --framec ./target/release/framec \
         --transpile-only`
    - All V3 module-path categories passed; one pre-existing Python CLI test
      (`basic_cli_compile`) failed due to an environment import-call issue,
      not related to the V3 scoping change.
  - Confirmed that the Python V3 scoping exec fixtures remain green under
    curated exec with the `0.86.56` binary.

## Impact
- Severity: Medium — previously blocked enabling Python V3 scoping fixtures
  for curated exec. With the fix in v0.86.55, these fixtures are now covered
  by exec tests, improving confidence in nested function + Frame glue
  interactions for Python.

## Technical Analysis
- The MIR and validator stages correctly recognize the Frame statements and
  nested function structure, and the fixture passes structural validation.
- The bug appears in the translation from MIR to Python source (PyExpanderV3 +
  splice), specifically when:
  - A nested `def` is present inside a handler, and
  - A Frame statement (`=> $^`) and additional native statements follow.
- The expander/splicer is not emitting the correct indentation levels when
  mixing nested `def` bodies, `system.return` updates, and Frame runtime calls.

## Proposed Solution
- Adjust the Python V3 emitter (PyExpanderV3 and/or splice integration) so that:
  - Nested `def` blocks preserve Python indentation semantics.
  - Frame statement expansions do not break indentation inside nested function
    bodies.
  - The generated code for scoping fixtures (function_scope/nested_functions/
    shadowing) is valid Python and executes as expected.
- Add an explicit regression assertion in the test runner by re‑enabling
  `# @exec-ok` on the Python v3_scoping fixtures once the generation is fixed.

## Verification Tests
- Re‑enable `# @exec-ok` for:
  - `framec_tests/language_specific/python/v3_scoping/positive/function_scope.frm`
  - `framec_tests/language_specific/python/v3_scoping/positive/nested_functions.frm`
  - `framec_tests/language_specific/python/v3_scoping/positive/shadowing.frm`
- Rerun:
  ```bash
  python3 framec_tests/runner/frame_test_runner.py \
    --languages python typescript \
    --categories v3_core v3_control_flow v3_scoping v3_systems \
    --framec ./target/release/framec \
    --run --exec-v3
  ```
  - Expectation: all three Python v3_scoping fixtures pass build/validate/run.
- Optionally add a small unit/regression test that inspects the generated
  `function_scope.py` to ensure the nested `def` body is correctly indented.

## Work Log
- 2025-11-22: Discovered while enabling exec for v3_scoping fixtures; nested
  `def f()` body in generated Python is not indented, leading to execution
  failure. Exec gating for Python v3_scoping fixtures was reverted to keep the
  suite green, and this bug was filed to track the emitter fix. — frame_transpiler assistant
