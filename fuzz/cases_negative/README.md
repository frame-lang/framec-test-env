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
E402, E403, E410, E413, E418, E420, E421, E601, E602, E603, E604,
E605, E614, E615.

`run_negative.sh` honors each fixture's own `@@target` directive when
present (falls back to CLI `-l <lang>`). E605 needs a static target
(Java in our fixture) since the check only fires for backends without
type inference.

## Codes intentionally not covered

- **E405 (state parameter arity mismatch)** and **E607 (state args on
  pop$)**. The V4 lexer conflates the relevant arg expressions into
  `Expression::NativeExpr` blobs so the validator can't see arity,
  and the framec implementations defer to the target compiler. A V5
  lexer split could re-enable these checks; until then there's no
  reachable fixture.
- **E000, E407, E408, E416, E417, E419, E501**. Less common — narrow
  target-specific (E501 GDScript) or only fire under combinations
  the existing cases already approximate. Add as needed when
  authoring fixtures that touch them.
