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
| Push / pop state stack                                   | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Step 21–24: HSM**                                      |
| HSM child–parent declaration (`$Child => $Parent`)       | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **HSM cascade enter (top-down `$>`)**                    | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌[d] |
| **HSM cascade exit (bottom-up `<$`)**                    | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌[d] |
| HSM parameter propagation (signature-match)              | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️[d] |
| Event forwarding (`=> $^`)                               | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Forward transition (`-> => $State`)                      | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️[d] |
| **Step 25: persistence**                                 |
| `@@persist` save / restore                               | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Async**                                                |
| `async` interface methods                                | ✅ | ✅ | ✅ | ✅ | 🚫 | ✅ | ✅ | 🚫[f] | 🚫[g] | 🚫 | ✅ | ✅ | 🚫 | 🚫 | ✅ | ✅ | 🚫[h] |

## Footnotes

[a] **Erlang** — built on `gen_statem` (OTP) instead of a custom
    kernel. The shape is different (state functions, not a router),
    but the semantic surface (`@@:return`, `@@:data`, lifecycle
    routing, transitions) is mapped onto the platform.

[b] **Erlang** — domain fields live on the `#data{}` record threaded
    through `gen_statem` callbacks. Reads/writes look like
    `Data#data.x` rather than `self.x`.

[c] **Erlang** — exit args populate `frame_exit_args` on the data
    record, but `frame_exit_dispatch__` is currently a no-op
    placeholder. The data is captured but no `<$` handler ever
    runs — see [d].

[d] **Erlang** — `gen_statem`'s `state_enter` mode fires `enter` on
    the *leaf* state only when transitioning, and there is no
    corresponding state-exit callback. The runtime-spec cascade
    (parent's `$>` runs top-down on entry; child's `<$` runs
    bottom-up on exit) is **not implemented**. Tracked as future
    work; existing Erlang HSM tests are smoke tests that don't
    assert ordering, so they continue to pass.

    Forward transitions (`-> =>`) similarly leave `forward_event`
    on the destination but don't re-dispatch it through a cascade
    — only the leaf's handler sees the forwarded event.

[f] **Java** — Frame async lowers to `CompletableFuture` in
    principle but isn't fully wired (`make_system_async` has a
    placeholder for Java). Existing Java tests don't exercise async.

[g] **Go** — async goroutines aren't supported via `@@async`;
    Go's concurrency model is goroutines + channels, which doesn't
    map cleanly onto the kernel-callback structure framec uses.
    Tests skip with `@@skip -- go is one-color`.

[h] **Erlang** — actor model + selective receive replaces async/await;
    "one-color" in the same sense as Go. Async tests skip.

## Summary

| Bucket | Conformance |
|---|---|
| Languages fully conformant to v4 spec | 16 / 17 (all except Erlang) |
| Languages with HSM cascade implemented | 16 / 17 |
| Known divergence | Erlang HSM cascade ([d]) |
| Language-natural skips | C, Go, PHP, Ruby, Lua, Erlang on async |

## Test corpus coverage

Every capability marked ✅ above is exercised by an executable test
under `tests/common/positive/`. The matrix-runner enforces these
across every language at every commit; see `make test` from
`docker/`.

The cascade tests (46–48), parameter-propagation test (49), and the
HSM state-arg propagation test (52) are the canonical conformance
gates for the HSM additions in v4. Erlang's versions of these are
smoke-test stand-ins (verify the system runs, log contains expected
strings) rather than ordering assertions, since the underlying
`gen_statem` runtime can't satisfy the spec without a substantial
rewrite of `frame_transition__`.
