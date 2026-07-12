# Intentional skip — language-specific async idiom

Language-specific async/concurrency idiom test. It exercises a construct particular to this backend's async model — e.g. C# exception filters / `Task` combinators, Kotlin dispatchers / `Mutex` / supervisor scope / cancellation, Swift `async let` / detached tasks / task groups, Dart futures / zones / completers, C++ coroutine throw-propagation / string-return lifetime, GDScript typed-await returns. These have no cross-language analogue, so the fixture is single-target by design.

See `docs/partial-coverage-audit.md`.
