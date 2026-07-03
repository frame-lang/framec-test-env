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

## Covered (16 fixtures, verified end-to-end on framec 4.6.1)

12 of the 14 RFC-0042 §9 diagnostic codes, plus a positive control:

| Fixture | Code | What it exercises |
|---|---|---|
| `mode_c_literal_at`         | E732 | unescaped literal `@` (framec#100 regression) |
| `mode_c_undeclared`         | E732 | Mode-C reference to an undeclared inner fsm |
| `mode_c_escaped_ok`         | *(ok)* | escaped `\@` is a literal — compiles clean (positive control) |
| `match_no_failure_branch`   | E701 | fallible match with a success transition but no failure branch |
| `bare_name_needs_self`      | E703 | bare field/param name in a body needs a `self.` prefix (§4.2) |
| `two_unlabeled_states`      | E704 | only the first state may be unlabeled |
| `missing_return_type`       | E705 | header lacks a return type / default |
| `domain_redeclares_param`   | E707 | a `domain:` field re-declares a parameter with a different type |
| `bad_input_alphabet`        | E713 | input alphabet not `bytes`/`char`/`token` |
| `non_regular_backref`       | E720 | backreference (non-regular construct) |
| `non_regular_lookahead`     | E720 | lookaround (non-regular construct) |
| `dfa_size_limit`            | E721 | regex compiles to a DFA past the configured state limit (`/.*a.{15}/`) |
| `charclass_on_token`        | E722 | char-class regex on a `token` alphabet |
| `duplicate_stage_label`     | E730 | a stage capture label used more than once in one state |
| `mode_c_alphabet_mismatch`  | E731 | Mode-C composition across mismatched alphabets |
| `transition_in_action_body` | E700 | `->` inside an action body (see E712 note below) |

## The two remaining §9 codes — framec observations, not fixture gaps

Both were run down to the framec source; neither is cleanly assertable at the
released-CLI boundary today, and each is a small framec-side finding worth a
follow-up issue rather than a test-env TODO:

- **E712** (transition inside an action body) — the parser *does* detect it
  (`fsm_parser/action_block_parser`: `error_code = "E712"`), but the CLI
  surfaces it as **E700** (the specific code is flattened parser→CLI). The
  `transition_in_action_body` fixture still guards the invariant (it asserts
  the construct is *rejected*, as E700), but the E712 code does not survive to
  the binary — arguably a framec bug (a diagnostic that doesn't reach the user
  by its documented code).
- **E723** (empty regex `//`) — the regex engine has the check
  (`fsm_regex`: `rejects_empty_with_e723`), but a literal `//` in `@@fsm`
  source is consumed by the **segmenter** and reported as **E001**
  (unterminated block) before the validator ever sees an empty pattern. So
  E723 is reachable by the engine's unit tests but not from CLI source in
  4.6.1.

## Adding a fixture

Write `<name>.fpy` with the minimal triggering `@@fsm` plus an
`# expect-error: EXXX` header (or `# expect-ok`), and re-run
`check_fsm_diagnostics.sh`. Craft the fixture so *only* the targeted construct
is invalid — otherwise framec errors on something else first and the test
passes for the wrong reason (e.g. failure branches must be `: -> $state`, and
body references to fields/params must be `self.<name>`).
