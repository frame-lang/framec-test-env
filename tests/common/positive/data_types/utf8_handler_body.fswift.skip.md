# Intentional skip — rust-only adversarial fixture

Exists to make a **defect in legacy framec 4.6.0.33 fail a test**, not to check a Frame feature.

Legacy's Rust auto-clone walker (`apply_rust_auto_clone`) copies a handler body with
`out.push(b as char)` — a Latin-1 widening — so any non-ASCII byte in native handler text is
corrupted. Twice, in fact: the body passes through two such copies, so `é` becomes `Ã©` becomes
`ÃƒÂ©`. The result is not valid Rust.

    oracle 4.6.0.33   let caf<C3 83 C2 83 C3 82 C2 A9> = 1;  -> FAIL [BUILD]
                                                                unknown start of token: \u{83}
    framec-ng         let caf<C3 A9> = 1;                    -> PASS

**Why rust-only:** the walker is Rust-specific, and `scripts/golden_run.py` currently has a
validated execution baseline only for rust. But the `as char` SHAPE is not rust-specific — the same
widening exists in the C++ and Java factory re-prefixers and in the shared expression expander, so
each of those languages wants its own version of this fixture once it has an execution gate.

**The interaction is load-bearing.** The `tag: String` domain field is what makes legacy walk the
body at all; delete it and the corruption vanishes. The bug needs non-Copy-field × non-ASCII-body,
which is why it survived a 352-fixture corpus that permuted single axes
(see `max_coverage/README.md` on framec#159).

Sibling: `data_types/utf8_string_literal.frs` pins the same defect class at a different site and a
different stage (ASSERT, not BUILD).
