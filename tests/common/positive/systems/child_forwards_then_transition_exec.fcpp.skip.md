# Intentional skip — C/Rust exec-ordering regression net

Execution-ordering regression net with `@@run-expect` output assertions (`FORWARD:PARENT` ×2 then `TRANSITION:`). It pins the exact forward-then-transition dispatch sequence on the two exec backends whose lowering is most divergent: C (pointer-based dispatch) and Rust (typed `StateContext` enum). The forward (`=> $^`) and transition (`-> $S`) semantics themselves are exercised across all 17 backends by the broader `control_flow/` and `systems/` suites; this fixture's distinct value is the exact-output contract on the C/Rust exec paths, which is not target-uniform.

See `docs/partial-coverage-audit.md`.
