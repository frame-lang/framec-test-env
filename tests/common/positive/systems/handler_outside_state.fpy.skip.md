# Intentional skip — Rust-only regression net

Rust-codegen-specific regression net. The bug or behavior it guards against was specific to Rust's borrow-checker, typed-domain handling, or factory-call path. Other backends didn't share the same code path.

See `docs/partial-coverage-audit.md`.
