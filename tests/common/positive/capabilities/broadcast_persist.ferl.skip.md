# broadcast_persist — Erlang skip

`@@[*persist]` broadcasts persist to every `@@system` in one module —
but Erlang is one system per file (E406; see max_erlang.ferl), so a
single-file two-system broadcast fixture cannot exist for this target.
A one-system file exercises nothing the per-system `@@[persist]`
fixtures don't already cover.

Broadcast semantics themselves are validated in-tree
(framec/tests/persist_affinity_127.rs) and the runtime round-trip is
exercised on the other 16 backends by this stem.
