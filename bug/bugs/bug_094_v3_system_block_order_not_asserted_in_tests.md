# Bug #094: V3 system block order not asserted in tests

## Metadata
```yaml
bug_number: 094
title: "V3 system block order not asserted in tests"
status: Fixed
priority: Medium
category: Validation
discovered_version: v0.86.60
fixed_version: v0.86.60
reporter: Codex
assignee:
created_date: 2025-11-26
resolved_date: 2025-11-26
```

## Description
The V3 validator (`ValidatorV3::validate_system_block_order_ast`) enforces a
canonical block order per system:

- `operations:`
- `interface:`
- `machine:`
- `actions:`
- `domain:`

and emits E113/E114 on violations. However, we do not currently have explicit
V3 fixtures that assert this behavior, and it is easy to land a mis-ordered
system (e.g., `domain:` before `machine:`) in Frame-owned code without tests
failing.

This surfaced while adding the Stage 14 `IndentNormalizer` system in
`framec_tests/language_specific/rust/v3_internal/indent_normalizer.frs`, which
originally declared:

```frame
system IndentNormalizer {
    interface:
        run()

    domain:
        ...

    machine:
        $Init { ... }
}
```

This violates the documented block order, but because we only compiled the file
and did not run validation (`--validate` / `--validation-only`) or have a
`v3_validator` negative fixture for block order, the issue was not caught by
tests.

## Reproduction Steps
1. Create a minimal V3 module with mis-ordered blocks, e.g.:
   ```frame
   @target python

   system S {
       interface:
           e()

       domain:
           x = 1

       machine:
           $A { e() { pass } }
   }
   ```
2. Run V3 validation on the module:
   ```bash
   framec compile --validation-only -l python_3 bad_block_order.frm
   ```
3. Observe whether E113 (`system blocks out of order`) is reported.

4. Note that we do not currently have a `v3_validator/negative` fixture that
   asserts this behavior for PRT languages, nor a shared-env test that checks
   block-order violations explicitly.

## Expected Behavior
- V3 validation should reject systems whose blocks appear out of order with
  E113 and/or E114.
- There should be explicit negative fixtures in `v3_validator/negative` for
  PRT languages (Python, TypeScript, Rust) that:
  - Use mis-ordered blocks.
  - Assert E113 via `@expect: E113`.
- Our test runner should route those fixtures through the module-validation
  path so that block order violations are caught in CI.

## Actual Behavior
- The validator code exists and can emit E113/E114, but:
  - There are no dedicated `v3_validator` negatives for block order.
  - It is possible to add Frame-owned systems with mis-ordered blocks (e.g.,
    `domain:` before `machine:`) and only notice when manually inspecting the
    grammar docs, not via tests.

## Impact
- Risk of Frame-owned systems drifting away from the documented grammar and
  relying on implicit behavior.
- Makes it harder to guarantee that block ordering rules remain enforced
  across refactors.

## Proposed Solution
- Add explicit block-order negative fixtures for PRT:
  - `framec_tests/language_specific/python/v3_validator/negative/system_block_order.frm`
  - `framec_tests/language_specific/typescript/v3_validator/negative/system_block_order.frm`
  - `framec_tests/language_specific/rust/v3_validator/negative/system_block_order.frm`
  Each fixture should:
  - Declare mis-ordered blocks (e.g., `domain:` before `machine:`).
  - Contain `@expect: E113`.
- Ensure the V3 runner routes these fixtures through `--validate` so E113 is
  surfaced and asserted in tests.
- Optionally, add a small shared-env regression script that compiles such a
  module with `--validation-only` and checks for E113 in stderr.

## Test Coverage
- [ ] Unit test added
- [x] Integration test added
- [x] Regression test added
- [x] Manual testing completed

## Work Log
- 2025-11-26: Noticed that `IndentNormalizer` was initially written with
  `domain:` before `machine:`, which violates the grammar but was not caught
  by existing tests. Filing this bug to add explicit block-order negatives and
  ensure `E113` is asserted in V3 validator suites for PRT languages.
- 2025-11-26: Added `system_block_order` negatives for PRT:
  - `framec_tests/language_specific/python/v3_validator/negative/system_block_order.frm`
  - `framec_tests/language_specific/typescript/v3_validator/negative/system_block_order.frm`
  - `framec_tests/language_specific/rust/v3_validator/negative/system_block_order.frm`
  Each fixture declares `domain:` before `machine:` and asserts `@expect: E113`.
- 2025-11-26: Fixed existing `actions_without_frame` positives in
  `v3_validator/positive` (Py/TS/Rust) to use the canonical block order
  (`machine:` before `actions:`).
- 2025-11-26: Verified with
  `python3 framec_tests/runner/frame_test_runner.py --languages python typescript rust --categories v3_validator --framec ./target/release/framec --transpile-only`:
  all PRT `v3_validator` suites now pass with E113 asserted where expected.
