# C++ Backend Bug Report — `std::bad_any_cast` in context parameter access

**Severity**: Medium — 2 test failures
**Tests**: `36_context_basic`, `37_context_reentrant`
**Binary**: `framec 4.0.0`

## Symptom

Runtime crash: `terminate called after throwing an instance of 'std::bad_any_cast'`

## Root Cause

The `@@:params["key"]` expansion in the C++ backend wraps the access in `std::any_cast<std::string>(...)`, but parameters are stored as their original type (int, string, etc.), not always as `std::string`.

### Generated code (line 102 of `36_context_basic.cpp`):

```cpp
// @@:return = @@:params["a"] + @@:params["b"]  (both are int)
_context_stack.back()._return = std::any(
    std::any_cast<int>(
        std::any_cast<std::string>(   // <-- BUG: "a" is int, not string
            _context_stack.back()._event._parameters["a"]
        )
    ) + std::any_cast<int>(
        std::any_cast<std::string>(   // <-- BUG: same
            _context_stack.back()._event._parameters["b"]
        )
    )
);
```

The handler dispatch already extracts params correctly at line 100-101:
```cpp
auto a = std::any_cast<int>(__e._parameters.at("a"));   // correct
auto b = std::any_cast<int>(__e._parameters.at("b"));   // correct
```

But `@@:params["a"]` in the body generates `std::any_cast<std::string>(...)` which crashes.

## Where in the code

`framec/src/frame_c/compiler/codegen/frame_expansion.rs`, line ~1814:

```rust
TargetLanguage::Cpp => format!(
    "std::any_cast<std::string>(_context_stack.back()._event._parameters[\"{}\"])",
    bare_key
),
```

This hardcodes `std::any_cast<std::string>` regardless of the actual parameter type.

## Fix Options

**Option A (recommended)**: Emit the local variable name directly (like the Rust fix). Since the handler dispatch already extracts `@@:params["a"]` into `auto a = std::any_cast<int>(...)`, the `@@:params["a"]` in the body should resolve to the local `a`, not re-access the context stack.

```rust
TargetLanguage::Cpp => bare_key.to_string(),
```

**Option B**: Remove the cast entirely and emit raw `std::any`:
```rust
TargetLanguage::Cpp => format!(
    "_context_stack.back()._event._parameters[\"{}\"]",
    bare_key
),
```
This defers the cast to the surrounding expression, but requires the caller to know the type.

## Verification

After fix, run:
```bash
FRAMEC_BIN=./framec-linux docker compose run --rm cpp
```

Expected: `137 passed, 0 failed, 0 skipped`
