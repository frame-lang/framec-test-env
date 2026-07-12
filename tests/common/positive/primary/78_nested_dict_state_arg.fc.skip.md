# Intentional skip — C has no native dict type

C has no built-in list/dict type (capability-matrix footnote [l]), so a list-/dict-typed *state argument* has no idiomatic C representation to thread through the typed state-context path this fixture probes. The 16 backends with native collections cover the compound-state-arg path uniformly; C's compound-type persistence is exercised separately by `102_persist_domain_list_dict` via the symbol-mangled pack/unpack helpers.

See `docs/partial-coverage-audit.md`.
