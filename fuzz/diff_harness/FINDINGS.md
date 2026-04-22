# Harness findings — Phase 1

Bugs surfaced by the differential trace harness during bring-up.
Each is a codegen divergence from the Python oracle on the canary case.

## 1. Ruby `restore_state` re-fires initial-state ENTER [FIXED]

**Severity:** codegen bug, cross-cuts every Ruby `@@persist` program.

**Symptom:** after `Canary.restore_state(blob)`, an extra `$>() $A`
fires before control returns to the caller. The restored instance ends
up in state `$B` (correct) but has executed `$A`'s enter handler as a
side effect.

**Root cause:** `restore_state` does `instance = Canary.new` which runs
the default constructor, which dispatches the initial state's enter
event. The compartment is then overwritten with the restored state,
but the enter-side-effect has already leaked.

```ruby
def self.restore_state(json)
    j = JSON.parse(json)
    instance = Canary.new                     # <-- fires ENTER $A
    instance.instance_variable_set(:@__compartment, …)
    instance
end
```

**Fix:** `restore_state` now uses `Canary.allocate` (Ruby's class-level
method that creates an instance without calling `initialize`) and
manually sets up `@__compartment`, `@_state_stack`, `@_context_stack`,
and `@__next_compartment`. The ENTER dispatch is skipped entirely.

**Oracle (Python) comparison:** Python's `restore_state` uses
`pickle.loads` which reconstructs the instance without calling
`__init__`. Ruby now matches that contract.

**Discovered by:** differential canary run, 2026-04-21. Fixed in
`framec/src/frame_c/compiler/codegen/interface_gen.rs` — the `Ruby`
branch of the persist methods generator. Ruby integration test matrix
unchanged at 215/0/1.

---

## 2. Lua `cjson` dependency not declared in emitted source

**Severity:** environment / packaging. Not strictly a codegen bug, but
the generated Lua file fails immediately on a vanilla Lua install
because it does `require("cjson")` without any up-front availability
check or fallback.

**Symptom:** `module 'cjson' not found` at save_state()/restore_state().

**Impact on harness:** Lua wrapper must install cjson before running;
documented in wrapper README. No framec action required unless we
decide to ship a pure-Lua JSON fallback.

---

---

## 3. Rust `@@:(int_literal)` boxes as `i32` but interface returns `i64` [FIXED]

**Severity:** codegen bug, any Frame source with `method(): int` that
uses `@@:(<integer literal>)` as the return value will panic at runtime.

**Symptom:** `thread 'main' panicked … Result::unwrap() on Err(Any …)`
at the interface method's `.downcast::<i64>().unwrap()` call.

**Root cause:** the generated handler body emits

```rust
let __return_val = Box::new(9) as Box<dyn std::any::Any>;
ctx._return = Some(__return_val);
```

Rust's integer literal defaults to `i32`. The enclosing method
signature is `pub fn go(&mut self) -> i64`, and the method's epilog
does `*ret.downcast::<i64>().unwrap()`. Downcast fails (boxed type is
`i32`, not `i64`) → unwrap panics.

**Why existing tests don't catch it:** `18_session_persistence.frs`
and most Rust persist tests use `str` returns, not `int`. The canary
is the first to combine `@@persist` with `int` returns in the same
recipe.

**Fix:** `rust_expand_box_return` and `rust_expand_box_return_bare` now
take the handler's `return_type` (same way the C backend already did
via `c_return_assign`) and a new `rust_wrap_for_boxing` helper wraps
the expression:
- `int` → `(expr) as i64`
- `float` → `(expr) as f64`
- string literal → `String::from(expr)` (existing behavior preserved)

Non-literal expressions that are already the correct type get a
redundant cast, which the Rust compiler elides.

**Discovered by:** differential canary run, 2026-04-21. Fixed in
`framec/src/frame_c/compiler/codegen/rust_system.rs`. Rust integration
test matrix unchanged at 218/0/0.

---

*(New findings append below as the harness expands to more backends.)*
