# Intentional skip — C-only test

C-only test for nested-function handling in native prolog. C is the only target where the issue surfaces; other backends handle nested helper functions via their native scoping rules without Frame-side intervention.

See `docs/partial-coverage-audit.md`.
