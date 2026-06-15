# `@@fsm` behavioral conformance matrix (RFC-0042)

Cross-language behavioral fixtures for the Frame `@@fsm` recognizer construct.
Each numbered fixture is authored **identically across all 17 target
languages** — same `@@fsm` block, same inputs, same expected observable result
fields (`accepted`, `cursor`, `return_value`, `reject_position`) — so the suite
proves that the *generated recognizers behave the same everywhere*, not merely
that codegen compiles. This complements the per-backend unit tests in the
`framec` repo (which check generation) with end-to-end runtime parity.

Each `NN_name.<ext>` file is `@@[target(...)]` + the shared `@@fsm` block + a
native epilog that instantiates the generated recognizer and asserts the
fields, printing `PASS: NN_name`. Run via the harness: `FRAMEC=<framec>
./run_tests.sh --category fsm` (or the hermetic docker matrix).

## Fixtures

| #   | Fixture | Feature exercised |
|-----|---------|-------------------|
| 100 | match_digits          | core DFA: literal class `/[0-9]+/`, cursor, accept/reject |
| 101 | alternation           | `cat\|dog`, leftmost/first-match |
| 102 | bounded_repetition    | `a{2,4}` greedy within bounds; `<2` rejects |
| 103 | greedy_longest        | `a*b` longest-match |
| 104 | start_anchor          | `^foo` (input start) |
| 105 | end_anchor            | `[0-9]+$` (input end) |
| 106 | interior_anchor       | `a$b` interior `$` (Pike VM zero-width Assert) |
| 107 | word_boundary         | `\bcat\b` edge boundaries (bytes) |
| 108 | lazy_quantifier       | `.*?,` leftmost-first (Pike VM) |
| 109 | inline_flag_caseless  | `(?i)cat` case-insensitive |
| 110 | capture_to_int        | stage capture `.n` + `to_int($s.n)` → return_value |
| 111 | inline_flag_dotall    | `(?s)a.b` — `.` matches `\n` |
| 112 | inline_flag_multiline | `(?m)a$` — `$` matches before `\n` (Pike VM LineEnd) |
| 113 | word_boundary_char    | `\bcat\b` on the `char` alphabet (Pike VM, Unicode `\w`) |
| 114 | unicode_class         | `\p{L}+` on `char` (opt-in `@@[allow(unicode_classes)]`) |
| 115 | transitions           | multi-state recognizer with failure branches |
| 116 | mode_c_composition    | `/@Inner/` sub-recognizer call-out |
| 117 | token_alphabet        | token-kind sequence `/IDENT LPAREN/` (the `token` alphabet) |

Coverage spans the full RE2 regular-language surface (literals, classes,
alternation, greedy/bounded/lazy quantifiers, edge + interior anchors, word
boundaries on bytes + char, Unicode classes, inline flags `(?i)`/`(?s)`/`(?m)`)
plus the Frame-specific constructs (stage captures, transitions, Mode C
composition) across all three alphabets (`bytes`, `char`, `token`).

## Documented per-language exceptions

These are design properties of the backends, not matrix gaps:

- **Erlang + Mode C (116):** Erlang is module-per-file; two `@@fsm` blocks emit
  two `-module` decls in one `.erl`, which `erlc` rejects. framec has no
  split-module emission for erlang multi-fsm, so 116 omits the erlang variant
  (erlang multi-fsm composition belongs in the `tests/erlang/multi/`
  convention).
- **Multibyte `char` input:** the `char` alphabet's element width differs by
  backend (codepoints on python/rust/go, UTF-16 units on js/java, bytes on
  c/cpp). The Unicode-class fixture (114) therefore matrix-tests ASCII letters
  (uniform everywhere); multibyte behavior is a per-backend concern.
