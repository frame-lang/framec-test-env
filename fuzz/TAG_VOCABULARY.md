# Fuzz tag vocabulary

Authoritative tag list for the unified runner contract
(see `TEST_INFRA_ROADMAP.md`). New tags added here BEFORE they're
used in any phase's `_index.tsv` or `.meta` files. The meta-runner
(`run_all.sh`) treats unknown tags as errors so vocabulary drift is
caught at the filter point.

## Tag categories

Tags are typed by their first segment when there's namespace risk
(e.g., `lang:erlang` vs `feature:hsm`); plain tags are unprefixed
when unambiguous. Most tags below are unprefixed.

### Language tags (one per case)

`python_3`, `javascript`, `typescript`, `ruby`, `lua`, `php`,
`dart`, `rust`, `go`, `swift`, `java`, `kotlin`, `csharp`, `c`,
`cpp`, `gdscript`, `erlang`

### Feature tags (one or more per case)

| Tag | What it covers |
|---|---|
| `persist` | `@@persist` save/restore (Phase 2) |
| `selfcall` | `@@:self.method()` reentrant dispatch (Phase 3) |
| `hsm` | Hierarchical state machines (Phase 4) |
| `operations` | Operation calls (Phase 5) |
| `async` | Async kernel + await (Phase 6) |
| `multisys` | Multi-system composition (Phase 7) |
| `negative` | Frame source that should fail framec validation (Phase 8) |
| `nested-syntax` | Recursive Frame-segment expansion (Phase 9) |
| `expr` | Expression-level codegen (Phase 10) |
| `pushpop` | `push$` / `pop$` modal stack |
| `lifecycle` | `$>` / `<$` enter/exit handlers |
| `state-args` | State arguments passed to states |
| `enter-args` | Args passed via `-> $S [args]` |
| `exit-args` | Args passed via `[args] -> $S` |
| `control-flow` | `if`/`while` in handler bodies |
| `transition` | `-> $State` flat or `=> $^` forward |
| `return-slot` | `@@:return` read/write |
| `params` | `@@:params["x"]` indexed access |
| `domain` | `self.field` reads/writes |
| `state-var` | `$.var` reads/writes |
| `system-param` | `@@system` parameter access |
| `const-field` | `const` domain fields |

### Depth tags (numeric, one per relevant axis)

| Tag | Meaning |
|---|---|
| `depth-0` | Flat / single-level |
| `depth-1`, `depth-2`, `depth-3` | Expression / call nesting depth |
| `hsm-1`, `hsm-2`, `hsm-3` | HSM hierarchy depth |
| `stmt-1`, `stmt-2`, `stmt-3` | Statement count in body |

### LHS / context tags

| Tag | Meaning |
|---|---|
| `return-lhs` | `@@:return = expr` |
| `dom-lhs` | `self.field = expr` |
| `sv-lhs` | `$.field = expr` |
| `local-lhs` | Native local var assignment |
| `void-lhs` | Bare expression statement (no LHS) |
| `in-if` | Expression placed inside `if` block |
| `in-while` | Expression inside `while` |
| `in-condition` | Expression as `if`/`while` condition |
| `after-call` | Statement appears after a self-call site |
| `before-transition` | Statement appears before `-> $S` |

### Tier tags (one per case, mutually exclusive)

| Tag | Meaning |
|---|---|
| `smoke` | Curated subset — runs in <2 min total matrix wall clock |
| `core` | Phase-specific essentials, runtime-asserted |
| `full` | Complete corpus for the phase |

A case tagged `core` is implicitly also `smoke` (smoke ⊆ core ⊆ full).
The runner's `--tier=smoke` flag matches `tags ∋ smoke`; `--tier=core`
matches `tags ∋ smoke ∨ tags ∋ core`; `--tier=full` matches everything.

### Behavior / shape tags (per-phase specific)

| Tag | Meaning |
|---|---|
| `save-restore` | persist round-trip pattern |
| `parent` | HSM parent-handler interaction |
| `uncle` | HSM cross-subtree transition |
| `linear` | Sequential statements, no branches |
| `if-guarded` | Single-arm `if` |
| `if-both-arms` | `if`/`else` |
| `await-N` | `await` count (e.g., `await-1`, `await-2`) |
| `phase-init` | Two-phase async init pattern |
| `panic` | Handler panic / exception pattern |
| `coercion` | Type coercion |
| `error-code-EXXX` | Negative test for a specific framec error (e.g., `error-code-E601`) |

## Filter syntax

Implemented in v1 of `run_all.sh`:

- Single tag: `--tag=hsm` — matches cases whose tag set contains `hsm`.
- AND-of-tags: `--tag=hsm,depth-2` — matches cases containing BOTH.
- Tier shorthand: `--tier=smoke` — equivalent to `--tag=smoke` (with
  the `core ⊆ ...` implicit expansion handled by the runner).
- Lang shorthand: `--lang=erlang` — equivalent to `--tag=erlang` but
  preferred for clarity and back-compat with existing runners.

NOT in v1 (deferred):
- OR-of-tags (`--tag=async|multisys`).
- Negation (`--tag=hsm,~depth-3`).
- Glob patterns.

If those become needed, extend the filter parser without breaking
the v1 contract.

## Adding tags

When a new phase or test pattern needs a tag not in this list:

1. Propose the tag in this doc (PR or commit alongside the case
   that needs it).
2. Update the relevant case generator to emit it.
3. Update meta-runner if it touches phase-list logic (rare).

The vocabulary is small intentionally — tags should be reusable
across phases. Resist adding case-specific tags; if you'd only ever
filter for one case, the case_id alone is sufficient.

## Validating tags

`run_all.sh` validates tags by checking each requested filter
against this doc's table. Unknown tag → error message + list of
similar known tags + abort. Implementation: parse the markdown,
extract the tag column, check membership.
