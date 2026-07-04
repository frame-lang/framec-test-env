# Intentional skip — no native inline string interpolation

This fixture exercises framec lowering a state-var (`$.x`) *inside* the target's native inline string-interpolation construct — Python f-strings, JS/Kotlin/Dart template literals, C# `$"…"`, Swift `\(…)`, Ruby `#{…}`, PHP `"{$…}"`. The backends skipped here have no inline interpolation syntax for that lowering to inhabit:

- **Rust** — `format!` is a macro, not inline string interpolation; framec rejects the f-string form (transpile error).
- **C, C++, Go, Java, Lua** — use printf-style / `String.format` / `%`-formatting, a different code path explicitly out of scope for this fixture.
- **GDScript** — uses `%`/`.format()`; it has no inline `${}`/`{}` interpolation, so framec emits literal braces that GDScript does not expand (verified empirically; this corrects the earlier audit note that listed GDScript as a port candidate).

The interpolation feature is covered on the eight backends with native inline syntax (C#, Dart, JS, Kotlin, Python, Ruby, Swift, TS) plus PHP.

See `docs/partial-coverage-audit.md`.
