# Phase 10 — Defects log

Authored autonomously during the overnight Phase 10 run. Every defect
the full-permutation expression fuzz surfaces lands here for morning
triage.

## Format

```
## D<N>: <one-line summary>

- Lang: <lang>
- Tier: smoke|full
- Case: <case_id>                   <!-- e.g. d2_sc_compute_plus_lit5 -->
- Tag: <equiv_class>                <!-- e.g. d2_selfcall_plus_lit -->
- Failure mode: transpile|compile|run|assert
- Reproducer: cases_perm/<file>
- Generated source: out_perm/<lang>/<case>/<file>
- Error: <verbatim error or assertion mismatch — first 3 lines>
- Suspected codegen path: <module:function or "unknown">
- Status: open | fix attempted | fixed | needs-review
- Notes: <free-form>
```

## Conventions

- Order in this file: most recent first (newest defects at top).
- `Status: needs-review` means the fix requires an architectural
  decision Mark should make.
- `Status: fixed` means the fix landed and the corresponding case
  passes; matrix verified clean.
- A defect that's a duplicate of a known one (same suspected codegen
  path) gets `Notes: dup of D<N>` instead of a new entry.

---

## D4: HSM cascade state-args not visible in parent state's handlers

- Lang: cross-backend (likely all 17, verified python_3)
- Tier: probe (matrix test 65 pulled before commit)
- Case: hand-crafted `65_hsm_forward_state_args.fpy`
- Tag: state-args, hsm-cascade, forward
- Failure mode: run (NameError on undefined local in generated handler)
- Reproducer: see "Probe" below
- Suspected codegen path: `state_dispatch.rs:1135` (`state_param_names` map)
- Status: needs-review
- Surfaced: 2026-04-30 during Phase 15 wave 3 (test 65)

### Probe

```frame
@@system StateArgFwd {
    interface:
        configure(t: int)
        process(): int
    machine:
        $Idle {
            configure(t: int) { -> $Active(t) }
            process(): int { @@:(0); return }
        }
        $Active => $Frame(threshold: int) {
            process(): int { => $^ }
        }
        $Frame {
            process(): int { @@:(threshold); return }
        }
    domain:
        n: int = 0
}
```

### Generated Python (defective)

```python
def _s_Frame_hdl_user_process(self, __e, compartment):
    self._context_stack[-1]._return = threshold  # NameError: 'threshold' undefined
    return
```

### Diagnosis

- Cascade syntax `$Active => $Frame(threshold: int)` parses `params=[threshold]`
  onto **$Active** (the child), not $Frame.
- `state_param_names["Active"] = ["threshold"]` → $Active's handlers get the
  prefetch.
- `state_param_names["Frame"] = []` → $Frame's handlers do **not** get the
  prefetch, even though its handler body references `threshold`.
- Runtime IS consistent: `__prepareEnter("Active", [t], [])` propagates
  `state_args = [t]` to **every** compartment in the cascade chain (including
  Frame's parent_compartment). So the value is available at runtime — the
  codegen just doesn't read it.

### Why this didn't surface before

Tests 4, 40, 61, 62 all read state-vars (`$.x`) or state-args from the
**leaf** (the state where the cascade arrow lives). The defect is specific
to: state-args declared via `=> $Parent(arg: T)` AND read from a handler
inside `$Parent`'s own body.

### Fix scope (decision needed)

Two options:

**A.** Extend `state_param_names` so $Frame inherits the params declared at
each child's cascade arrow. Single change in `state_dispatch.rs:1135`.
Affects all 17 backends symmetrically (they all read `state_param_names`).

**B.** Treat this as a Frame-language semantic restriction: state-args are
scoped to the leaf only, parent handlers cannot reference them. Add a
validator error (`E???: state-arg X is not in scope inside $Parent`) and
update docs.

The runtime already supports option A. Option B would require zeroing out
the parent compartments' state_args in `__prepareEnter`. Per the existing
"Phase 15 wave 3 — state-args carried through `=> $^` forwards" plan item,
the design intent appears to be option A.

Test 65 is parked until this lands. Regenerator-style cross-product testing
of HSM × state-args would benefit from the wave 3 axis being closed.

---

## D3: Swift rejects `self.n = self.n` (test corpus issue, not codegen)

- Lang: swift
- Tier: full
- Case: `dom_d1_dom_n`
- Tag: `dom_d1_fieldread`
- Failure mode: compile
- Reproducer: `cases_perm/dom_d1_dom_n.fswift`
- Generated source: `out_perm/swift/dom_d1_dom_n/dom_d1_dom_n.swift:251`
- Error: `error: assigning a property to itself | self.n = self.n`
- Suspected codegen path: not framec — Swift compiler rejects literal
  self-assignment by default.
- Status: needs-review
- Notes: This is a corpus issue, not a codegen bug. The test case
  evaluates `self.n = self.n` (a semantic no-op) at depth-1; 16 of 17
  backends accept it (it's a no-op assignment), Swift's compiler
  rejects it explicitly. Suggested fix: drop the receiver=LHS-target
  combinations from `enumerate_cases` since they don't exercise any
  codegen path the receiver=other-target combinations don't. Cleanest
  is to filter in `gen_perm.py:enumerate_cases` rather than per-lang.

---

## D2: Design question — semantics of multiple `@@:self.method()` calls inside one expression

- Lang: cross-backend (architectural)
- Surfaced by: D1 investigation
- Status: **resolved 2026-04-28**

**Decision (Mark)**: Option 2 — terminate execution at the **statement
execution context boundary**, not within an expression. A statement
containing embedded self-calls completes execution in its own context;
after the statement, the handler returns if any embedded call
transitioned the system. Single guard at end-of-statement, regardless
of LHS shape (`@@:return =`, `self.field =`, `$.field =`).

Rationale: the runtime spec already operates at statement boundaries
(`_transitioned` is checked between statements in the per-handler
emission). Inserting a guard mid-expression would require per-target
operator-precedence awareness — fragile codegen across 17 backends.
Aligning the guard with the language-natural statement boundary keeps
the codegen simple and matches Frame's "Oceans Model" delegation of
expression evaluation to the target language. Multi-self-call
expressions are also a code smell — natural Frame idiom uses one
self-call per statement, where the existing inter-statement guard
already fires correctly.

User-facing rule: **"the transition check fires at statement
boundaries, not within statements."** Users who want finer granularity
can split into separate statements:

```frame
$.tmp = @@:self.foo()        // separate statement; if foo()
$.x = $.tmp + @@:self.bar()  // transitioned, bar() never runs
```

Implemented as part of D1 fix below.

---

The Phase 10 v2 fuzz turned up a question that goes beyond D1's symptom.
Frame currently has *two different* implicit behaviors for embedded
self-calls depending on the LHS:

1. **`@@:return = self.a() + self.b()`** — both calls run unconditionally.
   No per-call transition guard. The whole expression evaluates, the
   result lands in the return slot. If `self.a()` transitioned, `self.b()`
   still runs (in the new state). This is the path through
   `frame_expansion.rs::ContextReturn` which lowers via
   `expand_expression()` and never sets `pending_guard`.

2. **`self.n = self.a() + self.b()`** — currently broken (D1). The
   intent of the codegen was to inject a per-call transition guard
   (`if _transitioned: return`) after each self-call segment via
   `pending_guard`, but that breaks the in-flight expression because
   the guard is a statement, not an expression.

The fix shape (option 2: defer guard until newline) makes (2) behave
the same as (1) — both calls run, then a single guard fires at
statement end. That's the *implementation-friendly* answer.

But the deeper question is: **what should Frame's contract for
embedded self-calls actually be?** Three plausible options:

a. **All calls run; guard at statement boundary.** Matches what
   `@@:return =` does today. Cheapest implementation. Risk: if
   `self.a()` transitions, `self.b()` runs in the new state and
   may behave unexpectedly (e.g., a method that was a no-op in
   state X is now a side-effect in state Y).

b. **Per-call abort via temp-bind hoist.** `self.n = self.a() + self.b()`
   becomes `tmp1 = self.a(); guard; tmp2 = self.b(); guard; self.n = tmp1 + tmp2;`.
   Expensive (~15 backends, each needs language-appropriate temp
   declaration). Most correct semantically. But: nothing in the
   runtime spec currently says self-calls inside expressions
   should abort early.

c. **Forbid embedded self-calls; require explicit intermediates.**
   Make the validator reject `self.n = self.a() + self.b()` and
   force the user to write `tmp = self.a(); self.n = tmp + self.b()`
   (or split further). Pushes the abort decision to the user.
   Most explicit. Breakage risk for existing user code.

Recommendation: discuss before shipping any of (a), (b), or (c).
The current state — implicit (a) for `@@:return =` and broken for
`self.field =` — is the worst of all worlds.

Related:
- D1 below (the symptom in `self.field = ...` LHS)
- Phase 9 p13 (Erlang-specific surface fix; closed)
- Erlang body-line pre-pass in `erlang_system.rs:erlang_process_body_lines_full`
  implements (b)-flavored hoist for Erlang only — accidental
  divergence from other backends' (a)-flavored behavior. Worth
  reconciling once the contract is decided.

---

## D1: Self-call in `self.field = expr` LHS breaks expression mid-line

- Status: **fixed 2026-04-28** (frame_expansion.rs, see "Fix" section
  below)

### Original symptom (before fix)

- Lang: python_3 (likely cross-backend; Phase 10 v2 only tested Python so far)
- Tier: full (v2 LHS variation)
- Cases: 18 distinct dom_* cases, all of shape
  `self.n = @@:self.<m1>() <op> <recv2>` where recv2 is either
  another self-call or a state-var read (`$.scache`).
  Examples:
    - `dom_d2_sc_compute_plus_sc_compute` → `self.n = self.compute() + self.compute()`
    - `dom_d2_sc_addone2_times_sv_scache` → `self.n = self.add_one(2) * $.scache`
- Tag: dom_d2_selfcall_<op>_(selfcall|fieldread)
- Failure mode: transpile generates SYNTACTICALLY BROKEN Python
- Reproducer: `cases_perm/dom_d2_sc_compute_plus_sc_compute.fpy`
- Generated source: `out_perm/python_3/dom_d2_sc_compute_plus_sc_compute/dom_d2_sc_compute_plus_sc_compute.py`
- Error: framec emits the transition guard mid-expression — line ends
  `self.n = self.compute() + ` followed by the guard `if … _transitioned: return` then orphan `self.compute()`.
- Suspected codegen path: `frame_expansion.rs:382-399` and the
  `pending_guard` logic at lines 240-269. The guard is set when a
  ContextSelfCall segment fires; the next NativeCode segment without a
  `\n` triggers the else-branch (lines 264-268) which emits guard
  immediately, breaking the in-flight expression.

  Critical detail: this only manifests for **native-code LHS**
  (`self.field =`) because that path is parsed as
  NativeCode → FrameSeg(self.method) → NativeCode(operator) →
  FrameSeg(self.method)... The Frame-segment-level LHS (`@@:return =`,
  `$.field =`) is processed differently (`ContextReturn` /
  `StateVarAssign` lower the WHOLE statement at once via
  `expand_expression`), so per-call guard injection doesn't apply
  and these cases work.

### Fix (shipped)

`framec/src/frame_c/compiler/codegen/frame_expansion.rs` — the
`pending_guard` emission in the NativeCode handler now defers until a
NativeCode segment with a newline arrives. When the next NativeCode
lacks a `\n` (continuation of the same statement, e.g. ` + 5`), the
guard stays pending and falls through to the next segment. The natural
statement-end newline triggers the emission.

Net effect: one transition guard at end-of-statement, never
mid-expression. A subsequent self-call segment may overwrite the
pending guard with its own — that's correct because `_transitioned`
is monotonic; a single statement-end check catches "any embedded call
transitioned the system."

### Verification

- v2 full tier across 17 langs: 17 × 460 = **7,820 / 7,820 passing**
  (all backends, including Erlang and Swift).
- Phase 9 Core: 68 / 68.
- 17-lang docker matrix: 3,800 passed, 0 failed.
- `cargo test --lib --release`: 363 passing.
- Clippy + fmt clean.

### Affected langs

All 15 backends that use the `pending_guard` mechanism in
`frame_expansion.rs`:
Python, JS, TS, Ruby, Lua, PHP, GDScript, Dart, Go, C, C++, Java,
Kotlin, C#, Swift, Rust.

Erlang was unaffected — its body-line pre-pass in
`erlang_system.rs:erlang_process_body_lines_full` already hoisted
self-calls into temp-binds, but for a different reason: Erlang's
record-update idiom `Data#data{n = expr}` requires `expr` to evaluate
first (Erlang is immutable; each `frame_dispatch__` returns a new
`Data`), so embedded self-calls must be sequenced as
`{Data1, R1} = ...; {Data2, R2} = ...; Data3 = Data2#data{n = R1 + R2}`.
The pre-pass is necessary for Erlang's mechanics, not a stricter
guard semantics. Both paths now produce statement-level transition
checks — the Erlang case-expression on `frame_current_state` after
each `frame_dispatch__` fires per call but is functionally identical
to the cross-backend single-end-guard because `_transitioned` is
monotonic. No reconciliation needed.

