# Intentional skip — multi-system per file (Java/Erlang)

Multi-system-per-file fixture. Java requires one public class per file (framec E430) and Erlang one `-module` per file (E431), so neither can host multiple `@@system` declarations in a single source file. Cross-system composition is exercised for both via the multi-source layouts under `tests/java/multi/` and `tests/erlang/multi/`. See capability-matrix footnotes [j]/[k].

See `docs/partial-coverage-audit.md`.
