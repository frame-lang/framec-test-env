# Bug #097: Rust @persist constructor arity mismatch ignored (TrafficLight)

## Metadata
```yaml
bug_number: 097
title: "Rust @persist constructor arity mismatch ignored (TrafficLight)"
status: Fixed
priority: High
category: CodeGen
discovered_version: v0.86.70
fixed_version: v0.86.70
reporter: Codex
assignee:
created_date: 2025-12-01
resolved_date:
```

## Description
The shared-env Rust persistence fixture `sandbox/persistence/traffic_light_persistence_rust.frm` declares `@persist system TrafficLight($(color), domain)` but the generated Rust code exposes `TrafficLight::new()` with **no parameters**. The fixture’s `main()` calls `TrafficLight::new()` successfully, so the missing constructor arguments are silently ignored instead of producing a compile-time arity error. This indicates the Rust codegen is dropping system parameters for `@persist` systems.

## Reproduction Steps
1) Use the shared reference compiler (v0.86.70):
   ```
   FRAMEC_BIN=bug/releases/frame_transpiler/v0.86.70/framec/framec
   OUT_DIR=$(mktemp -d)
   $FRAMEC_BIN compile -l rust -o "$OUT_DIR" sandbox/persistence/traffic_light_persistence_rust.frm
   ```
2) Inspect `$OUT_DIR/traffic_light_persistence_rust.rs`:
   - The generated impl includes `impl TrafficLight { pub fn new() -> Self { ... } }` with zero parameters.
   - The system signature in the FRM has two parameters: `$(color)` and `domain`.
3) (Optional) Attempt to call the constructor with no args in a Rust harness; it compiles, demonstrating the arity mismatch is not enforced.

## Build/Release Artifacts
- framec binary: `bug/releases/frame_transpiler/v0.86.70/framec/framec` (shared env reference)
- Fixture: `sandbox/persistence/traffic_light_persistence_rust.frm`
- Generated output (repro): `$OUT_DIR/traffic_light_persistence_rust.rs`

## Test Case
```frame
@target rust
@persist system TrafficLight($(color), domain) {
    interface: tick()
    machine: $Red($(color)) { tick() { -> $Red("red") } }
    domain: domain: &'static str = "red"
}
fn main() { let _tl = TrafficLight::new(); }
```

## Verification Tests
- None yet; fixture lives in shared env under `sandbox/persistence/traffic_light_persistence_rust.frm`.

## Expected Behavior
- The generated Rust constructor should require arguments matching the system parameters (e.g., `pub fn new(color: T, domain: U, ...)`), and calling `TrafficLight::new()` with zero args should fail to compile.
  - Alternatively, if defaults are allowed, the compiler should synthesize defaults for all params or enforce that the FRM signature aligns with the generated constructor arity.

## Actual Behavior
- `TrafficLight::new()` takes zero parameters in the generated Rust, so the caller can omit required system params without any compiler error. System parameters are effectively ignored for `@persist` Rust systems.

```
// Generated (excerpt)
impl TrafficLight {
    pub fn new() -> Self {
        Self {
            compartment: FrameCompartment{ state: StateId::default(), ..Default::default() },
            _stack: Vec::new(),
            domain:  "red",
        }
    }
}
```

## Impact
- **Severity**: High — breaks parity with the FRM signature and can hide missing inputs; `@persist` systems may be instantiated with default/incorrect data.
- **Scope**: Rust `@persist` systems; at least the shared TrafficLight fixture is affected.
- **Workaround**: None in codegen; user could manually edit generated code to add parameters, but that defeats determinism.

## Technical Analysis
- System parameters are not propagated into the generated Rust constructor for `@persist` systems, so arity enforcement is lost. The snapshot helpers still encode domain data, but the constructor does not accept the FRM-declared parameters.

### Root Cause
- To be determined; likely the Rust codegen path that synthesizes `new()` for `@persist` systems omits system params (and defaults).

### Affected Files
- `frame_transpiler` Rust codegen for `@persist` (constructor synthesis and/or system params plumbing).
- Shared fixture: `sandbox/persistence/traffic_light_persistence_rust.frm`.

## Proposed Solution
- Ensure system parameters are threaded into the Rust constructor signature for `@persist` systems (matching the FRM declaration), and fail builds when call sites omit required args.
- Add a shared-env harness to compile and `rustc` the generated output to assert constructor arity matches the FRM signature.

## Test Coverage
- [ ] Unit test added
- [ ] Integration test added
- [ ] Regression test added
- [ ] Manual testing completed

## Related Issues
- Rust persistence/snapshot parity work (v0.86.70 release).

## Work Log
- 2025-12-01: Reported mismatch; generated Rust constructor drops system params for `@persist` TrafficLight. — Codex
- 2025-12-01: Fixed in frame_transpiler v0.86.70:
  - System name detection now scans past annotations (e.g., `@persist system ...`), and system parameter parsing runs against the correct system name.
  - Rust codegen threads start/domain parameters into the generated constructor and seeds state_args from start params; domain params flow into struct fields.
  - Generated constructor for `TrafficLight` now requires `(color: serde_json::Value, domain: &'static str)`, so `TrafficLight::new()` with no args fails to compile as expected.

## Resolution
- Pending.
