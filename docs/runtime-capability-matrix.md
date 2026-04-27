# Runtime capability matrix

Per-language conformance to `docs/frame_runtime.md` (the v4 runtime
spec). Generated from a manual audit on 2026-04-26.

## Legend

- ✅ — fully implemented per spec
- ⚠️ — implemented with a known limitation (footnote)
- ❌ — not implemented; spec divergence
- 🚫 — language-natural skip (feature doesn't apply, e.g. async on a
  one-color language)

## Matrix

| Capability | Py | TS | JS | Rs | C | C++ | C# | Java | Go | PHP | Kt | Sw | Rb | Lua | Dart | GD | Erl |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Step 1–20: core runtime**                              |
| FrameEvent / FrameContext / Compartment classes          | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅[a] |
| Kernel + router + deferred transitions                   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅[a] |
| Lifecycle handlers `$>` / `<$` (flat states)             | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Domain fields                                            | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅[b] |
| State variables (`$.x`)                                  | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| State arguments (`$State(args)`)                         | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Enter args (`-> (args) $State`)                          | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Exit args (`(args) -> $State`)                           | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️[c] |
| Return values (`@@:return` / `@@:(...)`)                 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Default return values (interface defaults)               | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Cross-target return contract (dynamic / typed)           | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Actions / Operations                                     | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Context data (`@@:data`)                                 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| System parameters (`@@system Foo(args)`)                 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Self calls (`self.method(...)`)                          | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Self-call transition guard (post-call early return)      | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅[i] |
| Push / pop state stack                                   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Step 21–24: HSM**                                      |
| HSM child–parent declaration (`$Child => $Parent`)       | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **HSM cascade enter (top-down `$>`)**                    | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **HSM cascade exit (bottom-up `<$`)**                    | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| HSM parameter propagation (signature-match)              | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Event forwarding (`=> $^`)                               | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Forward transition (`-> => $State`)                      | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Step 25: persistence**                                 |
| `@@persist` save / restore                               | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Async**                                                |
| `async` interface methods                                | ✅ | ✅ | ✅ | ✅ | 🚫 | ✅ | ✅ | ✅[f] | 🚫[g] | 🚫 | ✅ | ✅ | 🚫 | 🚫 | ✅ | ✅ | 🚫[h] |

## Footnotes

[a] **Erlang** — built on `gen_statem` (OTP) instead of a custom
    kernel. The shape is different (state functions, not a router),
    but the semantic surface (`@@:return`, `@@:data`, lifecycle
    routing, transitions) is mapped onto the platform.

[b] **Erlang** — domain fields live on the `#data{}` record threaded
    through `gen_statem` callbacks. Reads/writes look like
    `Data#data.x` rather than `self.x`.

[c] **Erlang** — exit args populate `frame_exit_args` on the data
    record. `frame_exit_dispatch__` walks the HSM chain bottom-up
    and calls each layer's `frame_exit__<state>` helper, so child
    `<$` handlers fire and receive their declared params via
    positional extraction from the args map.

[f] **Java** — async-typed interface methods return
    `CompletableFuture<T>`, with bodies wrapping their result via
    `.completedFuture(...)`. The internal dispatch chain stays
    synchronous (the constructor fires the start-state's `$>`
    cascade directly, since two-phase init buys nothing on a
    sync runtime). Users `.get()` at the interface boundary.
    Implementation is `make_java_interface_async` in
    `framec_native_codegen/system_codegen.rs`. An `init()` method
    is also emitted for cross-language API parity (callers can
    write `system.init().get()` portably) — its body is a no-op
    completed-future, since the constructor already drove
    initialization. Tested by
    `tests/java/positive/async_basic.fjava` and
    `tests/common/positive/demos/19_async_http_client.fjava`.

[g] **Go** — async goroutines aren't supported via `@@async`;
    Go's concurrency model is goroutines + channels, which doesn't
    map cleanly onto the kernel-callback structure framec uses.
    Tests skip with `@@skip -- go is one-color`.

[h] **Erlang** — actor model + selective receive replaces async/await;
    "one-color" in the same sense as Go. Async tests skip.

[i] **Erlang** — the self-call transition guard is implemented via
    `gen_statem`'s native state-machine semantics rather than the
    `_transitioned` flag the other 16 backends use. After
    `frame_dispatch__`, generated code wraps the post-call
    statements in a `case Data#data.frame_current_state of
    <pre-call-state> -> [post-call code]; _ -> {next_state, ...}
    end` short-circuit. Functional contract identical (post-call
    code does not run after a transitioning self-call); structurally
    divergent (no `_transitioned` flag, no
    `if _context_stack[-1]._transitioned: return` shape).
    Implemented in `erlang_wrap_self_call_guards`
    (`framec/.../erlang_system.rs:1411-1589`); codegen's
    `generate_self_call_guard` returns empty for Erlang
    (`framec/.../frame_expansion.rs:4752`). The divergence is
    intentional — keeping `gen_statem` idioms is preferred over
    structural sameness. See `docs/erlang_alignment_requirements.md`
    in the framepiler repo for the path-to-alignment if structural
    consistency becomes a requirement.

## Summary

| Bucket | Conformance |
|---|---|
| Languages fully conformant to v4 spec | 17 / 17 |
| Languages with HSM cascade implemented | 17 / 17 |
| Known divergence | Erlang self-call guard mechanism ([i], structurally divergent but functional contract met) |
| Language-natural skips | C, Go, PHP, Ruby, Lua, Erlang on async |

## Test corpus coverage

Every capability marked ✅ above is exercised by an executable test
under `tests/common/positive/`. The matrix-runner enforces these
across every language at every commit; see `make test` from
`docker/`.

The cascade tests (46–48), parameter-propagation test (49), the
HSM state-arg propagation test (52), and the forward-transition
tests (19, 29) are the canonical conformance gates for the HSM
additions in v4. Erlang's `.ferl` variants run through a sidecar
driver convention (commit 5786312, 2026-04-27): if a
`<test>.driver.escript` exists alongside `<test>.ferl`,
`erlang_batch.sh` copies it to `run_test.escript` and uses it
instead of the auto-generated smoke-test driver. Tests 39, 47,
48, 49, 53 currently ship assertion-based drivers covering
self-call return-value propagation, HSM enter/exit cascade order
with parameter propagation, sibling transition under shared
parent, and the post-self-call transition guard. Tests without a
sidecar fall back to the smoke-test driver (call every export,
no ordering check).
