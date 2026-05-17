# Intentional skip — GDScript-specific regression

GDScript-only regression for the parameterized-child × domain-init fix (`#328` in framec memory). The bug was GDScript-codegen-specific; other backends already handled the case correctly.

See `docs/partial-coverage-audit.md`.
