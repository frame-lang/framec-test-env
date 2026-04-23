# Compile-Error Tests (Phase 8 — Negative Passthrough)

Tests that verify Frame sources **transpile successfully** but the
emitted native code **is rejected by the target toolchain** at either
compile time or runtime.

## Purpose — locking in the native-passthrough contract

Frame's architecture has a clean split:

- **Frame syntax** (`@@system`, `@@:self.method`, `$.var`, `-> $State`,
  `=> $^`, etc.) is translated per-target by framec.
- **Native syntax** in handler / action / operation bodies is passed
  through verbatim. Framec MUST NOT silently rewrite it to paper over
  the author's mistakes.

These tests author deliberately-bad native syntax and assert that:

1. Framec transpiles cleanly (the *Frame* structure is valid).
2. The target toolchain rejects the emitted code.

A test **FAILS** if:

- framec refuses to transpile (Frame-level regression), OR
- the target toolchain accepts the emitted code, meaning framec
  silently "fixed" the bad native syntax (passthrough regression).

## Running

```bash
./run_tests.sh
```

Environment variables:
- `FRAMEC` — path to the framec binary (default:
  `<repo>/framepiler/target/release/framec`).

Output is TAP 13 for CI integration.

## Naming convention

- `NN_<target>_<shortname>.f<ext>` — numbered by authoring order.
- Each test header includes a `NEGATIVE TEST:` comment explaining
  the specific passthrough-contract being locked in.

## Current tests

| Test | Target | Contract locked in |
|------|--------|-------------------|
| 02 | python | Bool literal `true` not rewritten to Python's `True` |
| 03 | rust | String literal `"hello"` not auto-wrapped to `String::from(...)` |
| 04 | javascript | Undefined identifiers not auto-declared / silently scoped |

## Adding a test

1. Pick a target and a specific *native* syntax that is valid Frame
   source structurally but fails when the target toolchain sees it.
2. Put the bad syntax somewhere framec will emit verbatim — usually a
   handler body, an action body, or an operation body.
3. If the error is runtime (NameError, TypeError, etc.), make sure the
   bad path is actually exercised — invoke the relevant interface
   method from the test's driver at the bottom of the file.
4. Run `./run_tests.sh`. A passing test prints
   `ok N - <name> (<target>) # correctly rejected at compile|runtime`.

## Supported extensions

Compile check: `.fc` `.fpy` `.fjs` `.fts` `.frs` `.flua` `.ferl`
`.fphp` `.frb`.

Runtime fallback (tried when compile accepts the code): `.fpy` `.fjs`
`.fphp` `.flua` `.frb`.
