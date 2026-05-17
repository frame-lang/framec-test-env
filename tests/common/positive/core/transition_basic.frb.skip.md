# Intentional skip — C-only regression net

C-codegen-specific regression net. The bug or behavior it guards against was specific to the C backend's pointer-based dispatch, native-function passthrough, or lifecycle-stack handling. Other backends didn't share the same code path.

See `docs/partial-coverage-audit.md`.
