# Intentional skip — async-native targets only

Persist × async cross-product fixture. Limited to backends with native async/await primitives that Frame's async codegen targets: C++ (coroutines), C# (async/await), GDScript (await), Go (goroutines + channels), Java (CompletableFuture), JS/TS (async/await), Kotlin (coroutines), Python (asyncio), Rust (async fn), Swift (async/await).

C, Dart, Erlang, Lua, PHP, Ruby do not have a consistent native-async target shape that Frame currently emits to (per the per-language capability matrix); no port for them.

See `docs/partial-coverage-audit.md`.
