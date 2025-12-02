# Bug #095: Rust V3 multi-state interface generates duplicate methods

## Metadata
```yaml
bug_number: 095
title: "Rust V3 multi-state interface generates duplicate methods"
status: Fixed
priority: Medium
category: CodeGen
discovered_version: v0.86.61
fixed_version: v0.86.61
reporter: Codex
assignee:
created_date: 2025-11-26
resolved_date: 2025-11-26
```

## Description
When compiling a V3 Rust system with an `interface` method implemented in
multiple states, the generator previously emitted **duplicate `fn run(&mut self)`
methods** on the same type, which is invalid Rust and fails to compile.

This surfaced while exploring Stage 14 (IndentNormalizer) and attempting
to model the algorithm with more than one state.

Minimal example `.frs` (Rust target):

```frame
@target rust

system S {
    interface:
        run()

    machine:
        $A {
            run() { println!("A"); }
        }
        $B {
            run() { println!("B"); }
        }
}
```

Compiling via the V3 module path:

```bash
framec compile -l rust test_states.frs -o test_states_rs
```

used to produce `test_states_rs/test_states.rs` with two `impl S` blocks both
defining `fn run(&mut self)`, e.g.:

```rust
impl S {
    fn run(&mut self) {
         println!("A"); 
    }
}

impl S {
    fn run(&mut self) {
         println!("B"); 
    }
}
```

which failed to compile under `rustc` with a duplicate method error.

## Fix

The V3 Rust module-path generator in `framec/src/frame_c/v3/mod.rs` was
updated so that:

- All handler bodies are first grouped by `owner_id` (interface/handler
  name) and `state_id` using a `BTreeMap<String, Vec<(Option<String>, String)>>`.
- The compiler now emits a **single** `impl S` block for handler methods,
  and for each handler name `h`:
  - If there is exactly one state-less handler (no `state_id`), it emits a
    simple method:
    ```rust
    fn h(&mut self) { /* body */ }
    ```
  - If there are handlers in multiple states, it emits a single method that
    dispatches on `self.compartment.state`:
    ```rust
    fn h(&mut self) {
        match self.compartment.state {
            StateId::A => { /* body for state A */ }
            StateId::B => { /* body for state B */ }
            _ => { }
        }
    }
    ```
- This preserves per-state behavior while ensuring there is only one
  public method per interface function on the system struct.

The runtime scaffold (StateId enum, FrameCompartment, `_frame_*` helpers)
remains unchanged; only the handler emission was restructured.

## Verification / Tests

- Main repo:
  - Built `framec` v0.86.61 with the new Rust V3 handler grouping.
  - Verified V3 PRT suites:
    ```bash
    python3 framec_tests/runner/frame_test_runner.py \
      --languages python typescript rust \
      --categories all_v3 \
      --framec ./target/release/framec \
      --transpile-only
    ```
    All existing PRT V3 tests (Python/TS/Rust) pass.
  - Manually compiled the minimal example:
    ```bash
    framec compile -l rust test_states.frs -o /tmp/test_states_rs
    rustc /tmp/test_states_rs/test_states.rs --crate-type lib -O -o /tmp/test_states.rlib
    ```
    `rustc` now succeeds; the generated `run` method contains a `match` on
    `self.compartment.state` instead of duplicate impls.

- Shared env regression script:
  - Added `bug/tests_095_rust_v3_multi_state_interface.sh` which:
    - Uses the reference `framec` binary
      (`bug/releases/frame_transpiler/v0.86.61/framec`).
    - Compiles the minimal `.frs` into `/tmp/.../out/test_states.rs`.
    - Compiles the generated Rust with `rustc`.
  - Running the script now prints `BUG095_OK`:
    ```bash
    FRAMEC_BIN=bug/releases/frame_transpiler/v0.86.61/framec \
      bug/tests_095_rust_v3_multi_state_interface.sh
    ```

## Impact

- Rust V3 multi-state systems with interface methods now generate valid
  Rust without duplicate public methods.
- This unblocks Stage 14 work that needs multi-state Rust machines (such as
  the IndentNormalizer) and moves Rust closer to parity with the Python/TS
  V3 runtime model.

