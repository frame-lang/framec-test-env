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

## Covered (16 fixtures, verified end-to-end on the authoritative local build — framec 4.6.0.6, which carries the framec#162 fix)

> Run the suite against the authoritative build (`~/.frame/local/bin/framec`),
> which carries framec#162 (E712) — the runner defaults to it.

13 of the 14 RFC-0042 §9 diagnostic codes, plus a positive control:

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
| `transition_in_action_body` | E712 | `->` inside an action body (RFC-0042 §3.7) |

## The one remaining §9 code — resolved as by-design, not a fixture gap

The two codes that weren't originally assertable at the CLI boundary were run
down to the framec source and filed as framec#162 / framec#163:

- **E712** — *fixed* (framec#162): the parser assigned `error_code = "E712"`
  but the CLI flattened it to E700. framec now surfaces E712 to the binary, so
  `transition_in_action_body` asserts the real code above. (Requires the
  framec#162 fix; on a framec without it the CLI reports E700.)
- **E723** (empty regex `//`) — *resolved won't-fix* (framec#163): the regex
  engine has the check
  (`fsm_regex`: `rejects_empty_with_e723`), but a literal `//` in `@@fsm`
  source is a **line comment** (RFC-0042 §3.5), not an empty regex — so an
  empty pattern can't be written as `//` and the E723 path is unreachable from
  source. Resolved as by-design: framec now emits an `@@fsm`-specific
  unterminated-block diagnostic that explains this, and RFC-0042 §6.10 records
  the empty-pattern rejection as a deliberate RE2 deviation. No fixture — there
  is no valid source that reaches E723.

## Adding a fixture

Write `<name>.fpy` with the minimal triggering `@@fsm` plus an
`# expect-error: EXXX` header (or `# expect-ok`), and re-run
`check_fsm_diagnostics.sh`. Craft the fixture so *only* the targeted construct
is invalid — otherwise framec errors on something else first and the test
passes for the wrong reason (e.g. failure branches must be `: -> $state`, and
body references to fields/params must be `self.<name>`).
