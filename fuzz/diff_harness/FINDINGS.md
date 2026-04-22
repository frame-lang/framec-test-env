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

---

## 4. PHP `restore_state` re-fires initial-state ENTER [FIXED]

**Severity:** same class as Ruby bug #1 — every PHP `@@persist` program
leaks initial-state enter side effects on restore.

**Symptom:** `Canary::restore_state($blob)` prints an extra
`TRACE: ENTER $A` before returning to the caller.

**Root cause:** generated `restore_state` used `new P()` which fires
the constructor, which dispatches the initial state's `$>()`
handler.

**Fix:** PHP now uses
`(new \ReflectionClass(P::class))->newInstanceWithoutConstructor()`
instead of `new P()`. This produces an instance without running
`__construct`. Instance props (`_state_stack`, `_context_stack`,
`__compartment`) are set up explicitly from the saved blob.

**Discovered by:** differential canary run, 2026-04-21. Fixed in
`framec/src/frame_c/compiler/codegen/interface_gen.rs` — PHP branch of
the persist generator. PHP Docker matrix unchanged at 209/0/4.

---

## 5. Swift `restoreState` re-fires initial-state ENTER [FIXED]

**Severity:** same class as Ruby/PHP — every Swift `@@persist` program
leaks the initial state's `$>()` handler on restore.

**Symptom:** Swift canary emitted `TRACE: ENTER $A` directly before
`TRACE: RESTORE ok`. Python emitted nothing between SAVE and RESTORE.

**Root cause:** generated `restoreState` used `let instance = Canary()`
which runs the default `init()`, which dispatches the initial-state
enter handler. Swift has no equivalent of Ruby's `allocate` or PHP's
`ReflectionClass::newInstanceWithoutConstructor`, so a second init
would be the idiomatic fix — but that would require non-trivial
refactoring of the Constructor codegen.

**Fix:** class-static flag `__skipInitialEnter` (declared in
`generate_swift_machinery`) gates the ENTER dispatch inside the
generated `init()`. `restoreState` sets the flag true, calls
`Canary()`, resets it false, then overwrites the compartment from
the saved blob. The flag is always emitted (default false) so
non-persist systems are unaffected.

Single-threaded re-entrancy caveat: calling `restoreState` from
inside an enter handler would race with the flag. Acceptable
constraint for `@@persist`; documented in the generator comment.

**Discovered by:** differential canary run, 2026-04-21. Fixed in
`framec/src/frame_c/compiler/codegen/interface_gen.rs` (Swift
restoreState emission) and `codegen/system_codegen.rs` (Swift
init_event_code wraps ENTER in `if !Canary.__skipInitialEnter`).
Swift Docker matrix unchanged at 207/0/0.

---

---

## 6. C# `RestoreState` re-fires initial-state ENTER [FIXED]

**Severity:** same class as Ruby/PHP/Swift.

**Fix:** use `RuntimeHelpers.GetUninitializedObject(typeof(P))` — the
modern .NET API that allocates an instance without running the
constructor. Instance fields (`_state_stack`, `_context_stack`) are
populated explicitly before the compartment is overwritten from the
saved blob.

Docker matrix unchanged at 213/0/0.

---

## 7. Java / Kotlin / C++ / GDScript — same restore-fires-ENTER bug [FIXED]

Audit of every remaining backend's `restore_state` path confirmed the
pattern: any backend whose generated code calls the public constructor
to obtain the instance *before* overwriting the compartment inherits
the same bug. The ones that dodged it did so by construction:

  * **Python** — `pickle.loads` bypasses `__init__`.
  * **JS / TS** — `Object.create(P.prototype)` bypasses the ctor.
  * **Go / Rust** — plain struct literal, no ctor to bypass.
  * **Dart** — a generated private `P._restore()` ctor already exists.
  * **Lua** — bare table + metatable, no ctor.

**Fix:** class-static flag `__skipInitialEnter` across Java, Kotlin,
C++, and GDScript. The flag is declared in each backend's
`generate_*_machinery` function (Java `private static boolean`,
Kotlin `companion object { @JvmStatic var }`, C++ `inline static
bool`, GDScript `static var`). The ctor's ENTER-dispatch body in
`system_codegen.rs` wraps the dispatch in `if !__skipInitialEnter`.
`restore_state` in each backend sets the flag true, calls the ctor,
resets false, then overwrites the compartment.

Swift uses the same pattern (fixed earlier). Ruby/PHP/C# use native
skip-ctor APIs (`allocate`, `ReflectionClass::newInstanceWithoutConstructor`,
`RuntimeHelpers.GetUninitializedObject`) where available — those
three are cleaner than the flag but the flag is portable everywhere
else.

**Verification:** full Docker matrix run pending at time of this
commit; will update FINDINGS once complete.

---

*(New findings append below as the harness expands to more backends.)*

---

## 9. Rust `str` default-value mismatch in domain block [FIXED]

**Severity:** framec Rust codegen. Any Frame source with a `str`-typed
domain var defaulted to an empty string literal produces uncompilable
Rust.

**Symptom:** Phase-2 persist generator writes `s: str = ""`. framec
Rust emits `pub s: String` in the struct (correct type mapping) but
the constructor initializes with the literal `""` (which is `&'static
str`, not `String`), so `rustc` rejects with:

```
error[E0308]: mismatched types
  --> src/main.rs:116:16
   |
116 |             s: "",
   |                ^^ expected `String`, found `&str`
```

**Root cause:** framec Rust's domain initializer emits the default
expression verbatim from the Frame source. The type has been mapped to
`String` but the default expression hasn't been wrapped in
`String::from(...)` / `.to_string()`.

**Existing tests don't hit this:** the demo suite uses
`user: String = String::new()` (user writes Rust-native) so the issue
only appears when the Frame source uses the portable `str` type name.

**Fix location:** codegen that emits domain initializers for Rust —
should wrap the default expression in `String::from(...)` when the
Frame declared type was `str` (and thus Rust field type is `String`)
and the default is a string literal.

**Fix:** `generate_rust_constructor` in `rust_system.rs` now routes
domain initializers through `rust_wrap_for_boxing` with the field's
declared type, so `s: str = ""` emits `s: String::from("")`. Also
fixed two adjacent Rust codegen bugs uncovered while iterating:
  - Handler-dispatch param unpacking was keyed on Rust type names
    (`i64`, `f64`, …), so a Frame `int` param fell through to the
    catch-all and was downcast as `String`. Added `int → i64` and
    `float → f64` normalization.
  - `rust_json_extract` / `rust_json_extract_unwrap` mapped Frame
    `int → i32`, but `RustBackend::convert_type` maps it to `i64`,
    so `restore_state` produced `expected i64, found i32`. Fixed by
    making `int` map to `i64` in the extract path.

Commit: `4b225f3`. Docker matrix Rust 218/218 unchanged; Phase-2
persist fuzz Rust 0/20 → 4/20 (remaining 16 fail on the separate
known String-clone-in-@@:() limitation).

---

## 10. Go domain `str` type not mapped to `string` [FIXED]

**Severity:** framec Go codegen. Same class as #9.

**Symptom:** `s: str = ""` in Frame domain → `s str` in generated Go
struct:
```
undefined: str
```

**Fix location:** Go struct field emission for domain vars. Should map
the Frame type `str` to `string`.

**Fix:** `GoBackend::emit_field` now routes the field type through
`self.map_type(raw_type)`, applying the `str → string` mapping that
was already present but unused for domain fields.

Commit: `1455d68`. Docker matrix Go 212/212 unchanged.

---

## 11. Go `self.` not rewritten to `s.` inside `@@:()` return expressions [FIXED]

**Severity:** framec Go codegen. Partial `self.` → `s.` rewrite.

**Symptom:** Frame source:
```
get_x(): int { @@:(self.x) }
```
Emits Go:
```go
s._context_stack[...]._return = self.x    // <-- should be s.x
```

Statement-body uses of `self.` (e.g. `set_x(v: int) { self.x = v; }`)
ARE correctly rewritten to `s.x = v`. Only the `@@:()` return-expansion
path misses the rewrite.

**Workaround in Frame source:** write the Go-native receiver directly
(`@@:(s.x)`), as `18_session_persistence.fgo` does. But that locks the
source to Go.

**Fix location:** whichever codegen path expands `@@:()` into the
`_return` assignment for Go — needs to apply the same
`self.` → `s.` rewrite the statement path uses.

**Fix:** All three Go return-assignment branches in
`frame_expansion.rs` (`@@:return = expr` assignment, bare `@@:(expr)`,
and the standalone-expression variant) now apply a
`expanded_expr.replace("self.", "s.")` pass, mirroring the Erlang
branch that does the analogous `Data#data.` rewrite. Statement-body
`self.` is still the user's responsibility in .fgo sources, but the
@@:() return path is now consistent.

Commit: `1455d68`. Full 8-backend Phase-2 fuzz (python_3, javascript,
typescript, ruby, dart, swift, csharp, go) at 648/648 trace-diff checks.

---

## 12. C# domain `str` type not mapped to `string` / `String` [OPEN]

**Severity:** framec C# codegen. Same class as #9, #10.

**Symptom:**
```
error CS0246: The type or namespace name 'str' could not be found
```
`str` in domain declaration is emitted verbatim; C# needs `string` or
`String`.

**Workaround:** Phase-2 harness `rewrite_trace` for C# does
`str` → `string` before passing source to framec. Documented as a
workaround pending the framec fix so the fuzz can run.

---

*(End of findings as of 2026-04-22.)*
