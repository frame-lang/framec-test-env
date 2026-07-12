# Intentional skip — statically-typed numeric erasure only

Statically-typed numeric-erasure round-trip: probes whether an integer survives a boundary that would erase it to a float, on the statically-typed backends where that ambiguity exists (C#, Go, Java, Kotlin, Swift). Dynamic backends preserve the runtime numeric type (nothing to erase), so the fixture is scoped to those five by design.

See `docs/partial-coverage-audit.md`.
