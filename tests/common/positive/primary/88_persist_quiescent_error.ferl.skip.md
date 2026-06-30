# Intentional skip — Erlang quiescent contract is implicit

Erlang enforces the quiescent contract implicitly via `gen_statem` run-to-completion semantics rather than an explicit `E700` throw: a handler that synchronously calls `save_state` on its own Pid deadlocks (the actor is busy processing the current event), times out after 5s, and the calling process crashes. Functionally equivalent to E700 (the operation fails on a contract violation) but the mechanism differs, so the explicit-error assertion this fixture makes does not apply. See capability-matrix footnote [q].

See `docs/partial-coverage-audit.md`.
