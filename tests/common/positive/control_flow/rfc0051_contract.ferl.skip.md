# rfc0051_contract — RED until RFC-0051 lands

The behavioral contract for RFC-0051 (structured handler-body lowering). Every
case asserts the **verified-correct** Frame semantics (`->` is an implicit
return). On the current Erlang **text-reparse pipeline** this fixture is RED:

- `elif_trail` (#125: else-if arm mutates + trailing mutates) — **fails to
  compile** (malformed `case`; the `Data` is not threaded through the
  non-terminal `case`).
- `read_after` (mutating `if` body + trailing read of the mutated field) —
  semantically wrong: the trailing is folded into the false arm (over-folding),
  so the read sees the pre-mutation value.
- `nested` (a no-else `if` whose body does not unconditionally exit, + trailing)
  — semantically wrong: `nested(1,0)` must run BOTH `self.d=1` and `self.e=1`,
  but over-folding skips the outer trailing.

The fold-correct cases (`ex` early-exit with a transitioning body, `xfer`,
`cross`) are already correct.

**Unskip when the RFC-0051 structural emitter lands** — it makes all ten
assertions pass by construction (early-exit is a node test, `Data` threading is
explicit SSA, every leaf yields a gen_statem tuple). Driver:
`rfc0051_contract.escript` (module `flow`), TAP 1..10.
