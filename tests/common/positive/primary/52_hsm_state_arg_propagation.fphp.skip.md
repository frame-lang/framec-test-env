# Intentional skip — Rust-only regression net

This fixture is a Rust-only regression net for the D5 cascade-visibility fix. The bug it guards against was specific to Rust's compartment-mutation path; other backends had different cascade behavior and aren't covered by the same regression.

See `docs/partial-coverage-audit.md` for the audit entry.
