# Negative `@@fsm` diagnostic suite (issue #20)

End-to-end coverage that the **released `framec` CLI rejects invalid `@@fsm`
input with the right diagnostic** — the half of the invariant *"framec never
emits code that doesn't compile"* that the positive `fsm/` matrix doesn't check.

This closes the gap that let **framec#100** ship: a `@@fsm` regex stage
`/@@target/` (unescaped literal `@`) was misparsed as a Mode-C call-out and
**emitted uncompilable code with no error**. The fix (framec#102) rejects it
with **E732**; this suite guards it (and the wider diagnostic family) at the
CLI boundary.

## Why one target, not ×17

`@@fsm` diagnostics are raised in the **validator, before codegen** — they are
target-independent. A negative fixture therefore runs on **one** target
(`python_3`), not the full matrix. This keeps the matrix cheap while giving the
same "diagnostic survives to the binary" guarantee the positive fixtures give
for behavior.

## How it works

Each fixture declares its expectation in a header comment:

```
# expect-error: E732    → framec must FAIL and the emitted error must contain E732
# expect-ok             → framec must SUCCEED (positive control)
```

`check_fsm_diagnostics.sh` transpiles each fixture with `framec` and scores it:

- **pass** — expected rejection with the declared code (or clean compile for
  `expect-ok`);
- **fail** — framec **accepted** an `expect-error` fixture (a silent
  miscompile — the #100 class of bug), or errored with the wrong / no code.

Output is TAP. Run:

```bash
./check_fsm_diagnostics.sh                    # uses framec from PATH
FRAMEC=/path/to/framec ./check_fsm_diagnostics.sh
```

## Covered (11 fixtures, verified end-to-end on framec 4.6.1)

| Fixture | Code | What it exercises |
|---|---|---|
| `mode_c_literal_at`        | E732 | unescaped literal `@` (framec#100 regression) |
| `mode_c_undeclared`        | E732 | Mode-C reference to an undeclared inner fsm |
| `mode_c_escaped_ok`        | *(ok)* | escaped `\@` is a literal — compiles clean (positive control) |
| `match_no_failure_branch`  | E701 | fallible match with a success transition but no failure branch |
| `two_unlabeled_states`     | E704 | only the first state may be unlabeled |
| `missing_return_type`      | E705 | header lacks a return type / default |
| `bad_input_alphabet`       | E713 | input alphabet not `bytes`/`char`/`token` |
| `non_regular_backref`      | E720 | backreference (non-regular construct) |
| `non_regular_lookahead`    | E720 | lookaround (non-regular construct) |
| `charclass_on_token`       | E722 | char-class regex on a `token` alphabet |
| `mode_c_alphabet_mismatch` | E731 | Mode-C composition across mismatched alphabets |

## Follow-up — RFC-0042 §9 codes not yet seeded here

These have unit-test coverage inside framec (`fsm_validator/mod.rs`); the
end-to-end fixture is deferred until the exact source trigger is pinned down —
each of my attempts on framec 4.6.1 either compiled clean or surfaced a
different code:

- **E703** (bare name where `self.`/`$stage.cap` required) — attempted bare
  capture ref, compiled clean.
- **E707** (domain/param type mismatch) — reduce returning `int` under a `bool`
  header compiled clean.
- **E712** (transition inside an `actions:` body) — the `@@system` analogue
  surfaces as **E401**, not E712; the `@@fsm` trigger is unclear.
- **E721** (DFA-size limit) — large bounded repetitions drive DFA construction
  long before a size check fires (framec spins rather than rejecting fast).
- **E723** (empty regex `//`) — hits the segmenter first as **E001**
  (unterminated block), not the validator.
- **E730** (duplicate stage label) — a fixture with a repeated `$label:`
  compiled clean.

To add one: write `<name>.fpy` with the minimal triggering `@@fsm` plus an
`# expect-error: EXXX` header, and re-run `check_fsm_diagnostics.sh`.
