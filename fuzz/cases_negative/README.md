# Phase 8 — negative fuzz cases

Hand-authored Frame sources that **must** be rejected by `framec`
with a specific validator error code. Each case file's prolog
declares its expected code with the directive:

```
# @@expect-error: E<NNN>
```

The runner (`fuzz/run_negative.sh`, plus the in-process classifier
in `fuzz/run.sh::transpile_case`) compiles each case via
`framec -l python_3` and verifies framec exited non-zero with
stderr containing the declared code. Anything else — wrong code,
or transpile success — is FAIL.

## Why hand-authored, not generated

Per `fuzz/FUZZ_PLAN.md` Phase 8: the expected error message and
exact code are tied to the validator's specific rejection paths.
Generators would hit a combinatorial explosion across error codes
+ message phrasings; one fixture per code is more compact and
direct.

## Adding a case

1. Pick an unverified validator error code (run `grep '"E[0-9]'
   framec/src/frame_c/compiler/frame_validator.rs` for the list).
2. Author a minimal `.fpy` (10–20 lines) that triggers the code.
3. Add `# @@expect-error: E<NNN>` to the prolog.
4. Verify locally:

   ```
   framec compile -l python_3 -o /tmp/check <case>.fpy
   ```

   The output should include `Compilation failed:` and `E<NNN>:`.
5. Add the file; `run_negative.sh` discovers it automatically.

## Coverage

Currently covers (sorted): E111, E113, E114, E116, E117, E400, E401,
E402, E403, E405, E407, E410, E413, E416, E417, E418, E419, E420,
E421, E501, E601, E602, E603, E604, E605, E614, E615.

`run_negative.sh` discovers any `cases_negative/*.f<ext>` fixture,
honors each one's `@@target` directive, and falls back to the CLI's
`-l <lang>` value otherwise. The runner glob accepts arbitrary Frame
extensions (`.fpy`, `.fjava`, `.frs`, `.fts`, etc.) so per-language
fixtures are first-class. E605 needs a static target (Java in our
fixture) since the check only fires for backends without type
inference. E407 ships per-language fixtures because each backend
implements `skip_nested_scope` against its own closure syntax.

### E407 — Frame statement inside nested function scope

Fires from the unified scanner via the per-backend `skip_nested_scope`
implementation. Each backend's fixture exercises the closure syntax
specific to that language:

| File                                          | Closure shape       |
|-----------------------------------------------|---------------------|
| `e407_java_lambda.fjava`                      | `() -> { ... }`     |
| `e407_typescript_arrow.fts`                   | `() => { ... }`     |
| `e407_javascript_arrow.fjs`                   | `() => { ... }`     |
| `e407_csharp_lambda.fcs`                      | `() => { ... }`     |
| `e407_rust_closure.frs`                       | `\|\| { ... }`        |
| `e407_cpp_lambda.fcpp`                        | `[](){ ... }`       |
| `e407_go_func.fgo`                            | `func() { ... }`    |
| `e407_php_closure.fphp`                       | `function() {...}`  |
| `e407_lua_function.flua`                      | `function() ... end`|
| `e407_kotlin_lambda.fkt`                      | `{ x -> ... }`      |
| `e407_swift_closure.fswift`                   | `{ x in ... }`      |

Python (lambda body is expression-only, can't host Frame statements),
Ruby (multiple ambiguous forms), Dart (`(args) { body }` is identical
to `if (cond) { body }`), and GDScript (no native closure syntax)
default-return `None` from `skip_nested_scope` and so don't ship
E407 fixtures. C has no closures at all.

### Transition-arg arity codes (E405, E417 transition form, E419)

These three checks validate the three sites where a transition can
supply args to a receiver:

| Syntax           | Receiver                     | Code  |
|------------------|------------------------------|-------|
| `(args) -> $T`   | source state's `<$(...)`     | E419  |
| `-> (args) $T`   | target state's `$>(...)`     | E417  |
| `-> $T(args)`    | target state's state params  | E405  |

E419 and the transition-form of E417 are EventParam-backed, so trailing
defaults relax the lower bound (caller may omit defaulted params).
E405 is StateParam-backed and StateParam carries no defaults today,
so its check is exact-count.

The "no receiver" fixtures (`e419_exit_args_no_handler.fpy`,
`e417_enter_args_transition_no_handler.fpy`,
`e405_state_args_no_params.fpy`) cover the case where a transition
supplies args to a receiver that doesn't exist at all. Undersupply
and oversupply variants exist for the EventParam-backed codes;
StateParam-backed E405 just needs the no-params and count-mismatch
forms.

All three checks were unreachable before v4 because the pipeline
parser dropped exit/enter/state args into `NativeExpr` blobs before
the validator saw them. `enrich_handler_body_metadata` (in
`framec/src/frame_c/compiler/native_region_scanner/mod.rs`) re-runs
the unified scanner on each handler body and writes the parsed
`exit_args`/`enter_args`/`state_args` strings onto the AST between
parse and validate. That makes the existing arity code reachable.

## Codes intentionally not covered

- **E607 (state args on pop$)**. Implemented but the existing
  `e607_state_args_on_pop.fpy` covers it in spirit through the
  pop$ branch of `validate_transition` — promote a dedicated
  fixture if a regression ever slips through.
- **E000, E408**. Less common — only fire under combinations the
  existing cases already approximate. Add as needed when authoring
  fixtures that touch them.
- **E407 on Python / Ruby / Dart / GDScript**. These backends'
  `skip_nested_scope` returns `None` by design — Python lambda
  bodies are expression-only (no statement-level Frame markers
  possible), Ruby has too many closure forms to detect cleanly,
  Dart's `(args) { body }` is byte-identical to `if (cond) { body }`,
  and GDScript closures rely on indentation. Frame source
  authored against these targets is not protected against the
  silent-corruption hazard for those specific patterns; the
  validator has no scope-detection there.
