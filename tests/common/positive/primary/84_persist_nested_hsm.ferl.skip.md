# Intentional skip — Erlang one module per file

Erlang requires one `-module` per file (framec E431), so a multi-system / nested-`@@SystemName` fixture cannot be expressed in a single `.ferl`. The same behavior is exercised end-to-end via the multi-source layout under `tests/erlang/multi/` (one `.ferl` per module + a shared `driver.escript`); persist recurses through child gen_statem process trees. See capability-matrix footnotes [k]/[p].

See `docs/partial-coverage-audit.md`.
