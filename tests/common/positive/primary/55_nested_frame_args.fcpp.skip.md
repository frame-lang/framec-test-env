# Intentional skip — Python-only smoke fixture

Python-only smoke fixture for nested `@@SystemName($(arg))` call resolution. No regression coverage value on other backends since the codegen path is target-agnostic.

See `docs/partial-coverage-audit.md`.
