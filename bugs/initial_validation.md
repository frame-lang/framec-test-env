# Framepiler Test Results — Bug Report

**Binary**: `framec 4.0.0` (built from `/Users/marktruluck/projects/framepiler`)
**Test Infrastructure**: Docker containers, 16 languages validated
**Date**: 2026-04-06

## Summary

| Language | Pass | Fail | Skip | Status |
|---|---|---|---|---|
| Python | 161 | 0 | 0 | PASS |
| TypeScript | 143 | 0 | 0 | PASS |
| JavaScript | 137 | 0 | 0 | PASS |
| Rust | 136 | 11 | 0 | **FAIL** — context + async codegen |
| C | 146 | 1 | 0 | **FAIL** — context codegen |
| C++ | 135 | 2 | 0 | **FAIL** — context codegen |
| C# | 133 | 0 | 0 | PASS |
| Java | 133 | 0 | 0 | PASS |
| Go | 133 | 0 | 0 | PASS |
| PHP | 133 | 0 | 0 | PASS |
| Kotlin | 133 | 0 | 0 | PASS |
| Swift | 127 | 0 | 0 | PASS |
| Ruby | 136 | 0 | 0 | PASS |
| Erlang | 131 | 0 | 5 | **COMPILE-ONLY** — no runtime execution |
| Lua | 136 | 0 | 0 | PASS |
| Dart | 132 | 0 | 4 | PASS |
| GDScript | — | — | — | SKIPPED (x86-only container, ARM64 host) |
| **Total** | **2186** | **14** | **9** | |

---

## Bug 1: Rust backend — `Box<dyn Any>` not `Clone` or `Display`

**Severity**: High — blocks 11 tests (all context + async tests)
**Affected tests**: `36_context_basic`, `37_context_reentrant`, `async_basic`, `async_enter_exit`, `async_hsm_forward`, `async_multi_system`, `async_push_pop`, `async_reentrant`, `async_return_values`, `async_transition`, `async_two_phase_init`

**Root cause**: The Rust backend generates code that stores context data as `Box<dyn Any>` but then attempts to:
1. Clone it (via derive or explicit `.clone()`) — `Box<dyn Any>` does not implement `Clone`
2. Format it with `Display` (via `format!()` or string interpolation) — `Option<Box<dyn Any>>` does not implement `Display`

**Compile errors**:
```
error[E0277]: the trait bound `Box<dyn Any>: Clone` is not satisfied
error[E0277]: `Option<Box<dyn Any>>` doesn't implement `std::fmt::Display`
```

**Expected fix**: The Rust backend needs to either:
- Use `Arc<dyn Any>` instead of `Box<dyn Any>` (implements `Clone`)
- Use the enum-of-structs pattern already established for compartments (avoids `dyn Any` entirely)
- For Display: downcast to concrete type before formatting, or implement a custom Display wrapper

---

## Bug 2: C backend — void* to int implicit cast in context parameter access

**Severity**: Medium — blocks 1 test
**Affected test**: `37_context_reentrant`

**Root cause**: The C backend generates `ContextReentrantTest_PARAM(self, "a")` which returns `void*`, but passes it directly to a function expecting `int`. C requires explicit casting.

**Compile error**:
```
error: passing argument 2 of 'ContextReentrantTest_inner' makes integer
       from pointer without a cast [-Wint-conversion]
  expected 'int' but argument is of type 'void *'
```

**Expected fix**: The C backend needs to generate explicit casts when context parameters are used as typed arguments: `(int)(intptr_t)ContextReentrantTest_PARAM(self, "a")` or use a typed accessor macro.

---

## Bug 3: C++ backend — `std::any` not directly concatenatable with `std::string`

**Severity**: Medium — blocks 2 tests
**Affected tests**: `36_context_basic`, `37_context_reentrant`

**Root cause**: The C++ backend generates code like:
```cpp
std::string result = std::string("Hello, ") + _context_stack.back()._event._parameters["name"] + "!";
```

The `_parameters["name"]` returns `std::any`, which cannot be directly concatenated with `std::string`. It needs `std::any_cast<std::string>()` first.

**Compile error**:
```
error: no match for 'operator+' (operand types are 'std::string' and 'std::any')
```

**Expected fix**: The C++ backend needs to emit `std::any_cast<T>()` when accessing context parameters in expressions that expect typed values.

---

## Issue 4: Erlang backend — no runtime test execution

**Severity**: Medium — 131 tests compile but never execute
**Affected**: All 131 Erlang tests (5 skipped separately)

**Root cause**: Two issues:

1. **Test files lack native epilog**: The `.ferl` test files contain only the `@@system` block — no native Erlang code after it that starts the gen_statem and calls interface methods. Every other language (Python, TS, Java, etc.) has test harness code in the native epilog. Erlang tests have none.

2. **Generated module has no `main/0`**: The Erlang backend generates a `gen_statem` behaviour module with `start_link/0` and interface methods, but no standalone entry point. Unlike Python (which generates a class you can instantiate inline), Erlang gen_statem modules must be started as processes.

**What "compile-only" means**: `erlc` successfully compiles the `.erl` to `.beam` — this validates the generated Erlang syntax is correct. But the code is never executed, so semantic correctness (transitions, state variables, etc.) is unverified.

**Expected fix**: Each `.ferl` test file needs a native Erlang epilog that:
```erlang
main() ->
    {ok, Pid} = ModuleName:start_link(),
    Result = gen_statem:call(Pid, interface_method),
    %% assert results
    io:format("PASS~n"),
    init:stop().
```

This affects 131 test files. Could be scripted by parsing the `@@system` interface definitions and generating the harness code.

---

## Notes

- All failures verified on both Docker containers and native macOS — these are transpiler codegen bugs, not test infrastructure issues.
- The context system (`@@:params`, `@@:return`, `@@:data`) was added on 2026-04-04. The affected backends (Rust, C, C++) haven't been updated to handle context types correctly.
- Python, TypeScript, JavaScript, Go, Java, C#, PHP, Kotlin, Swift, Ruby, Lua, Dart all pass 100% — the context system works correctly in these backends.
