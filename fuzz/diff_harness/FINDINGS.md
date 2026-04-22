# Harness findings — Phase 1

Bugs surfaced by the differential trace harness during bring-up.
Each is a codegen divergence from the Python oracle on the canary case.

## 1. Ruby `restore_state` re-fires initial-state ENTER

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

**Fix:** `restore_state` needs to bypass the initial-state enter
dispatch. Options:
  - Use `allocate` instead of `new` (Ruby's class-level method that
    creates an instance without calling `initialize`), then manually
    set up the @__compartment and context stack.
  - Add an internal constructor mode (e.g. `initialize(skip_enter:
    true)`) used only by restore_state.

**Oracle (Python) comparison:** Python's `restore_state` uses
`pickle.loads` which reconstructs the instance without calling
`__init__`. No enter fires. That's the contract Ruby violates.

**Discovered by:** differential canary run, 2026-04-21. Run with
`fuzz/diff_harness/run_diff.py canary/canary.frame --langs
python_3,ruby`.

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

## 3. Rust `@@:(int_literal)` boxes as `i32` but interface returns `i64`

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

**Fix:** emit `Box::new(9_i64)` (or use `as i64` cast) when the
enclosing method's Frame return type is `int`. The box-to-type match
is required for `downcast` to succeed.

**Discovered by:** differential canary run, 2026-04-21. Run with
`fuzz/diff_harness/run_diff.py canary/canary.frame --langs
python_3,rust`.

---

*(New findings append below as the harness expands to more backends.)*
