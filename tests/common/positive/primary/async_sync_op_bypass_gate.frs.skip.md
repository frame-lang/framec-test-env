# Intentional skip — async fixture split across test trees

Cross-backend async behavioral fixture whose coverage is **split across the common and language-specific trees**: the Python, TypeScript, JavaScript, Rust and Java variants live under `tests/<lang>/positive/` (all five present there), while the six typed backends here carry the `common/positive/primary/` copy. The remaining backends — C, Go, PHP, Ruby, Lua — are one-color (no async/await), so the fixture does not apply.

See `docs/partial-coverage-audit.md`.
