# Intentional skip — rust-only adversarial fixture

This fixture exists to make a **defect in legacy framec 4.6.0.33 fail a test**, not to check a
Frame language feature. It pins one path: `@@:(<string literal>)` with non-ASCII content, where
legacy rebuilds the literal byte-by-byte as `push(b as char)` — a Latin-1 widening that emits `é`
(C3 A9) as `Ã©` (C3 83 C2 A9). The emitted program compiles and runs and returns the wrong string.

Measured on this construct:

    oracle 4.6.0.33   String::from("cafÃ©")     -> FAIL [ASSERT], 4 assertions
    framec-ng         String::from("café")     -> PASS

**Why rust-only, for now:** the detector is `scripts/golden_run.py` (emit → build → RUN → assert)
driven against the oracle through `scripts/framec-oracle-shim.sh`. Only rust has a validated
execution baseline there today. The widening is **not** rust-specific — it is the same
`as char` shape found at ~9 sites across the codegen tree, including a lexer-level one upstream of
all 17 backends — so ports here are wanted as soon as each language has an execution gate that can
actually assert on a returned value.

Porting it: keep the two literals (2-byte U+00E9 and 3-byte U+2192) and keep the **byte-count and
char-count assertions**, not just string equality. A double-encoded `é` still reads as text, so an
eyeball or a `grep` misses it; the counts do not.

See `data_types/utf8_string_literal.frs` and `max_coverage/README.md#R4`.
