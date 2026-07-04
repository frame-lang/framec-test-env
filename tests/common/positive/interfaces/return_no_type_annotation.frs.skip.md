# Intentional skip — dynamic-typed targets only

Tests Frame's allowance of return without a type annotation on the interface method. Only meaningful on dynamically typed targets (Python, JS, Ruby, Lua, PHP, GDScript) where return types are inferred at runtime. Typed targets (Java, Kotlin, Swift, C#, C, C++, Go, Rust, Dart, TS) require explicit return-type annotations as part of their host-language grammar — a Frame fixture missing the annotation cannot transpile.

See `docs/partial-coverage-audit.md`.
