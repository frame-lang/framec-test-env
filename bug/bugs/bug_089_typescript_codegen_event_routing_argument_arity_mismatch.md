# Bug #089: TS codegen emits mismatched argument arity in `_event_` routing

## Metadata
bug_number: 089
title: TS codegen emits mismatched argument arity in `_event_` routing
status: Duplicate
priority: High
category: CodeGen
discovered_version: v0.86.54
fixed_version: v0.86.54
reporter: vscode_editor (Codex)
assignee: framepiler team
created_date: 2025-11-21
resolved_date: 2025-11-21

## Description
In the V3 TypeScript generator, the per-system router method:

```ts
_frame_router(__e: FrameEvent, c?: FrameCompartment, ...args: any[]): any { ... }
```

incorrectly forwarded only a single argument to `_event_` handlers for interface methods with
parameters, regardless of the actual parameter count. This resulted in mismatched arity between
interface wrappers, router dispatch, and `_event_` handler signatures.

Before the fix, the router emitted code like:

```ts
case "runtimeMessage": return this._event_runtimeMessage(__e, _c, args[0]);
```

even when the handler had multiple parameters. This could not correctly forward multiple arguments,
and also interacted poorly with the spread-based calling convention.

## Reproduction Steps
1) In the Frame Transpiler repo, with `framec v0.86.54` **before** this fix:
   - Run the V3 CLI TS tests:
     ```bash
     python3 framec_tests/runner/frame_test_runner.py \
       --languages typescript \
       --categories v3_cli \
       --framec ./target/release/framec \
       --transpile-only
     ```
2) Observe failures for fixtures that rely on interface methods with parameters:
   - `actions_and_domain_emit_issues` (runtimeMessage payload forwarding)
   - `adapter_protocol_minimal` (runtimeMessage payload forwarding)
   - `multi_state_interface_router` (payload-bearing handlers)
3) Inspect the generated TS router:
   - `framec_tests/generated/cli/typescript/actions_and_domain_emit_issues.ts`
   - Note that for parameterized methods it uses:
     ```ts
     case "runtimeMessage": return this._event_runtimeMessage(__e, _c, args[0]);
     ```
   - Even if the interface would logically support multiple arguments, only `args[0]` is forwarded.

## Build/Release Artifacts
- framec binary (fixed):
  - `../frame_transpiler/target/release/framec` (v0.86.54, build 48)
- Generated TS used to validate the fix:
  - `framec_tests/generated/cli/typescript/actions_and_domain_emit_issues.ts`
  - `framec_tests/generated/cli/typescript/adapter_protocol_minimal.ts`
  - `framec_tests/generated/cli/typescript/multi_state_interface_router.ts`

## Expected Behavior
- For each interface method with N parameters, the router should:
  - Accept `...args: any[]`.
  - Forward exactly N arguments to the corresponding `_event_` handler:
    ```ts
    case "foo": return this._event_foo(__e, _c, args[0], args[1], ..., args[N-1]);
    ```
- For parameterless interface methods, the router should call `_event_foo(__e, _c)` with no extra
  arguments.

## Actual Behavior (pre-fix)
- Router dispatch used only a boolean flag `has_params` per method and always forwarded:
  - `args[0]` when `has_params == true`, regardless of the actual parameter count.
- This caused:
  - Incorrect arity when methods accepted multiple parameters.
  - Inconsistent semantics for fixtures that relied on the full argument list.

## Technical Analysis
- The V3 TS generator (`framec/src/frame_c/v3/mod.rs`) already computed a `params` string for each
  handler group and then derived `param_idents` from it using `ts_param_idents(params)`.
- However, the router only tracked a boolean `has_params` and emitted:

  ```rust
  for (hname, has_params) in router_cases {
      if has_params {
          module.push_str(&format!(
              "      case \"{}\": return this._event_{}(__e, _c, args[0]);\n",
              hname, hname
          ));
      } else {
          module.push_str(&format!(
              "      case \"{}\": return this._event_{}(__e, _c);\n",
              hname, hname
          ));
      }
  }
  ```

- This ignored the actual arity implied by `param_idents`.

## Proposed Solution
- Track the **arity** (number of parameters) per interface method instead of just a boolean flag.
- Emit router cases that:
  - Call `_event_foo(__e, _c)` when `arity == 0`.
  - Call `_event_foo(__e, _c, args[0], args[1], ..., args[N-1])` when `arity == N > 0`.

## Fix Summary / Duplicate Of
- This report is a duplicate of the canonical Bug #089 file:
  `bug_089_typescript_codegen_mismatched_event_routing_arity.md` (status: Closed).
  Please refer to that canonical bug for the validated fix and verification details.
- In `framec/src/frame_c/v3/mod.rs` (TypeScript branch):
  - Replaced `router_cases: Vec<(String, bool)>` with:
    - `router_cases: Vec<(String, usize)>`.
  - After computing `param_idents`, derived an arity:
    ```rust
    let arity = if param_idents.is_empty() {
        0
    } else {
        param_idents
            .split(',')
            .filter(|s| !s.trim().is_empty())
            .count()
    };
    router_cases.push((hname, arity));
    ```
  - Updated router emission to:
    ```rust
    for (hname, arity) in router_cases {
        if arity == 0 {
            module.push_str(&format!(
                "      case \"{}\": return this._event_{}(__e, _c);\n",
                hname, hname
            ));
        } else {
            let mut call = format!(
                "      case \"{}\": return this._event_{}(__e, _c",
                hname, hname
            );
            for idx in 0..arity {
                call.push_str(", args[");
                call.push_str(&idx.to_string());
                call.push(']');
            }
            call.push_str(");\n");
            module.push_str(&call);
        }
    }
    ```

## Verification Tests
- Re-ran the TS V3 CLI suite:
  - `python3 framec_tests/runner/frame_test_runner.py --languages python typescript --categories all_v3 --framec ./target/release/framec --transpile-only`
  - All TypeScript V3 CLI tests now pass, including:
    - `actions_and_domain_emit_issues`
    - `adapter_protocol_minimal`
    - `multi_state_interface_router`
- Manually inspected generated routers:
  - `framec_tests/generated/cli/typescript/actions_and_domain_emit_issues.ts`
  - `framec_tests/generated/cli/typescript/adapter_protocol_minimal.ts`
  - `framec_tests/generated/cli/typescript/multi_state_interface_router.ts`
  - Confirmed:
    - Parameterless methods use `_event_foo(__e, _c)`.
    - Parameterized methods use `_event_foo(__e, _c, args[0], ...)` with the expected arity.
- Shared adapter smoke:
  - `FRAMEC_BIN=../frame_transpiler/target/release/framec ./adapter_protocol/scripts/run_adapter_smoke.sh`
  - Output: `ADAPTER_SMOKE_OK` with `framec 0.86.54`.

## Closure Requirements (shared env + adapter)
- **Compiler/toolchain version**
  - Use `framec v0.86.54` or later where router arity is tracked and emitted correctly.
- **Adapter FRM coverage**
  - Rebuild the adapter TS from the current FRM:
    - `FRAMEC_BIN=/Users/marktruluck/projects/frame_transpiler/target/release/framec`
    - `OUT_DIR=$(mktemp -d)`
    - `$FRAMEC_BIN compile -l typescript -o "$OUT_DIR" src/debug/state_machines/FrameDebugAdapter.frm`
  - Ensure the FRM still includes any multi-parameter interface methods you care about (e.g., payload-bearing handlers).
- **TypeScript compile**
  - Use a `tsconfig.json` under `$OUT_DIR` consistent with Bugs #084/#088 to map `frame_runtime_ts` to the shared d.ts.
  - Run:
    - `/Users/marktruluck/projects/framepiler_test_env/adapter_protocol/node_modules/.bin/tsc -p "$OUT_DIR/tsconfig.json"`
  - Requirement: `tsc` must not report arity-related errors (e.g., `TS2556` from spread or mismatched argument counts) for the router or `_event_` methods.
- **If mismatches are observed**
  - Attach to this bug:
    - The `_event_...` signatures and router cases from the generated `FrameDebugAdapter.ts`.
    - The corresponding handler headers from `FrameDebugAdapter.frm`.
    - The exact `tsc` error messages.
  - This will allow us to confirm whether the remaining mismatch is:
    - In the FRM (e.g., header updated but not call sites), or
    - In a corner case of the router generator not covered by the existing fixtures.

## Work Log
- 2025-11-21: Observed TS2556 errors and incorrect argument forwarding when running the TS V3 CLI
  suite; identified router arity mismatch as root cause. — framepiler team
- 2025-11-21: Implemented arity-aware router emission and validated against generated TS for
  adapter-like fixtures and multi-parameter handlers. — framepiler team
- 2025-11-21: Re-ran full V3 TS/Python test suite and adapter smoke; all green. — framepiler team
- 2025-11-21: Marked as Duplicate of `bug_089_typescript_codegen_mismatched_event_routing_arity.md` to avoid split tracking. — vscode_editor

## Resolution
- Tracked under the canonical Bug #089 file `bug_089_typescript_codegen_mismatched_event_routing_arity.md`.
