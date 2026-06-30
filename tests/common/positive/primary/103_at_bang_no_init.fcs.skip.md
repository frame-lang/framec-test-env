# Intentional skip — @@! sigil smoke on D7 reference backends

This fixture exists to exercise the `@@!Foo()` no-init *sigil* itself (RFC-0017 D7) — the syntactic form that allocates a naked shell without running the start state's `$Start(...)` body or `$>` enter handler. It is scoped to the D7 reference backends the sigil shipped on (Python, Rust, Java, Kotlin, Swift, Erlang) plus GDScript.

On the remaining backends, the restore-without-init *behavior* that `@@!` enables is already covered end-to-end by the persist suite (tests 23-25, 51, 56-60, 83-88, 93, 96, 98, 99): `@@[load]` allocates the shell and populates it from the serialized blob without re-firing the enter cascade. Re-testing the sigil on every backend would duplicate that coverage without exercising a new code path.

See `docs/partial-coverage-audit.md`.
