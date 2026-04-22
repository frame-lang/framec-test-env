# Differential Trace Format — v1

Every backend in the differential fuzz harness must produce **byte-identical
stdout** for the same Frame source + event sequence. This doc nails down
the format so a divergence is unambiguously a codegen bug, not a format
disagreement.

## The contract

The program emits **trace lines** — one line per semantic event, in the
order they occur. A trace line is:

```
TRACE: <event-type> <payload>
```

- `TRACE:` literal, followed by one space.
- `<event-type>` is one of the fixed keywords below.
- `<payload>` is event-specific, using the value-formatting rules in
  the next section.
- Line terminator is `\n` (LF only — no CR). Windows-native runtimes
  must strip CR before emit.
- No trailing whitespace on any line.

Any stdout line **not** starting with `TRACE: ` is ignored by the
differ — the wrapper may use it for PASS/FAIL / diagnostics. Event
traces are the diff corpus.

## Event types

| Keyword     | Payload                          | Emitted when                                        |
|-------------|----------------------------------|-----------------------------------------------------|
| `CALL`      | `<method>(<arg>, <arg>, …)`      | An interface method is invoked (before dispatch).   |
| `RET`       | `<value>` or `void`              | An interface method has returned.                   |
| `ENTER`     | `$<StateName>`                   | Before a state's `$>()` handler body runs.          |
| `EXIT`      | `$<StateName>`                   | Before a state's `<$()` handler body runs.          |
| `STATE`     | `$<StateName>`                   | After every transition settles (one per transition).|
| `DOMAIN`    | `<field>=<value>, <field>=<value>` | On explicit `dump_domain()` wrapper calls only.   |
| `SAVE`      | `ok` or `err:<reason>`           | After `save_state()` succeeds/fails.                |
| `RESTORE`   | `ok` or `err:<reason>`           | After `restore_state(blob)` succeeds/fails.         |
| `NOTE`      | `<freeform ASCII>`               | Wrapper-level breadcrumb (use sparingly).           |

CALL/RET pairs are emitted by the **wrapper**, not the generated Frame
code — the wrapper wraps each dispatch. ENTER/EXIT/STATE are emitted
by **the generator** inserting `print` statements in handler bodies
(since Frame has no built-in hook).

## Value formatting

To survive cross-language rendering without divergence, only these
types are permitted in fuzz cases:

### Integers
- Decimal digits, optional leading `-`.
- **No** leading `+`, no leading zeros, no thousand separators, no
  hexadecimal, no scientific notation.
- Range restricted to `[-1_000_000, 1_000_000]` in generators —
  conservatively within `i32` for every backend.
- Examples: `0`, `-1`, `42`, `-999000`.

### Strings
- Double-quoted: `"..."`.
- ASCII-only, `0x20` through `0x7E`, excluding `"` and `\`.
- **No** escape sequences — generators avoid backslash and double-
  quote entirely.
- Examples: `""`, `"hi"`, `"abc 123 xyz"`.

### Booleans
- Lowercase literal: `true` or `false`. No other spelling.

### State names
- Prefixed with `$`, matches the Frame source (CamelCase): `$Idle`,
  `$LoggedIn`.

### void returns
- The literal word `void` (e.g. `RET void`).

### Forbidden in fuzz-generated programs
- Floating-point values (language variance is inherent).
- Lists, maps, tuples, objects in any trace payload.
- Null/nil/None — generators use sentinel integers or empty strings.
- Unicode non-ASCII.
- Very large integers (see range above).
- Bytestrings and binary blobs (except inside a `@@persist` save blob,
  which is NEVER diffed — only the post-restore behavior trace is).

## Canonical example

Frame source fragment (what the generator would emit):

```frame
@@target python_3
@@persist
@@system Canary {
    interface:
        go(): int

    machine:
        $A {
            $>() { print("TRACE: ENTER $A") }
            go(): int {
                print("TRACE: STATE $B")
                @@:(7)
                -> $B
            }
        }
        $B {
            $>() { print("TRACE: ENTER $B") }
            go(): int { @@:(9) }
        }
}
```

Wrapper drives it with `go()` → `go()` → `save_state` → `restore_state`
→ `go()`. Expected trace (byte-verified against the Python backend —
this is the oracle):

```
TRACE: ENTER $A
TRACE: CALL go()
TRACE: STATE $B
TRACE: ENTER $B
TRACE: RET 7
TRACE: CALL go()
TRACE: RET 9
TRACE: SAVE ok
TRACE: RESTORE ok
TRACE: CALL go()
TRACE: RET 9
```

Any backend that produces a different trace fails.

## Notes

- **RESTORE does NOT re-fire ENTER.** `restore_state()` rehydrates the
  instance; it is not a transition, and the contract is that the
  already-entered state does not re-enter. A backend that re-fires
  ENTER on restore is diverging from the oracle and should be filed
  as a codegen bug.
- **Order of STATE vs ENTER vs RET when a handler transitions:**
  STATE is emitted by the generator immediately before `->`. After
  `->` the runtime fires the new state's ENTER. Then the original
  handler returns — so `RET` is always last in the tuple. (EXIT from
  the old state would fire between STATE and ENTER if `<$()` is
  defined on the old state.)
- **Async ordering:** async backends must preserve the single-threaded
  sequential semantics — no interleaving between a CALL and its
  matching RET. If a backend's async dispatch leaks interleavings,
  that's a bug the fuzzer is designed to catch.

## Versioning

This is v1. Incompatible changes bump to v2 and update every wrapper
template in lockstep. The generators stamp the trace format version
at the top of each emitted test file (`# TRACE_FMT: v1`) so a runner
can assert compatibility.
