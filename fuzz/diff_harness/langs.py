"""Per-language configuration for the differential trace harness.

Each `Lang` encodes how to:
  - Target the backend with framec (`target`, file `ext`).
  - Compile the emitted source to a runnable artifact (`compile_cmd`).
  - Run the artifact with captured stdout (`run_cmd`).
  - Express the trace-capture harness at the end of the Frame source
    (`render_harness`, which takes the fuzz sequence and returns the
    native epilog).

The persist API is inconsistent across backends (some snake_case, some
camelCase, some PascalCase, one uses `load_state` instead of
`restore_state`). That's captured per-Lang.

NOTE: compile_cmd / run_cmd are designed to work on macOS (dev host).
For CI parity, the Docker matrix will wrap these with container
invocations; same binary names, so the Lang config stays portable.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional


@dataclass
class Lang:
    name: str                     # framec `-l` target
    ext: str                      # Frame source extension (fpy, fjs, …)
    out_ext: str                  # Generated source extension (py, js, …)
    # Optional compile step after framec emits source (e.g. javac, rustc).
    compile: Optional[Callable[[Path], List[str]]] = None
    # Command to run the artifact; receives the path framec wrote.
    run: Optional[Callable[[Path], List[str]]] = None
    # Persist API naming quirks (see FUZZ_PLAN.md table).
    save_method: str = "save_state"
    restore_call: str = "restore_state"
    # Canary harness (pre-Phase-2, kept for the existing canary runner).
    # Takes an ignored placeholder string and returns the native epilog.
    render_canary: Optional[Callable[[str], str]] = None
    # Per-harness-kind renderer. Keyed on `meta["harness_kind"]` from
    # the case's `.meta` sidecar — one entry per fuzz Phase:
    #   "persist"     (Phase 2) — save/restore round-trip with normalized
    #                 TRACE lines for every step of the sequence.
    #   "selfcall"    (Phase 3) — `@@:self.<method>()` guard semantics.
    #   "hsm"         (Phase 4) — HSM parent-forwarding semantics.
    #   "operations"  (Phase 5) — `operation` blocks.
    #   "async"       (Phase 6) — `async` handler await sequences.
    #   "multi_system"(Phase 7) — system-in-domain composition.
    # Each renderer takes the case's meta dict and returns the native
    # epilog spliced after the @@system block. Every renderer MUST
    # produce a byte-identical trace to the Python oracle's output for
    # the same case.
    renderers: Dict[str, Callable[[dict], str]] = field(default_factory=dict)
    # Rewriter: turn a Python-syntax trace line like
    # `print("TRACE: ...")` into the backend's equivalent. Applied to
    # the @@system block by run_fuzz. Default assumes `print(...)` is
    # valid in the target (true for Python, Lua, Swift, GDScript, Dart).
    rewrite_trace: Callable[[str], str] = lambda s: s
    # Native prolog injected BEFORE the @@system block, AFTER the
    # @@target directive. Use for `package main` (Go), `require 'json'`
    # (Ruby), etc. Kept separate from the harness because framec
    # requires these as pre-system native code.
    prolog: str = ""
    # Docker image to use for compile + run when the backend's toolchain
    # or libraries aren't present on the host (e.g. `org.json` for Java /
    # Kotlin, `cjson` for Lua, C++23 on macOS). When set, the runner
    # bind-mounts the case's output directory at `/work` inside the
    # container and executes compile/run there — `compile` and `run`
    # callables should reference files under `/work`.
    docker_image: Optional[str] = None
    # Backends that don't fit the `compile(path) + run(path)` template
    # (e.g. Erlang renames the emitted file to match `-module(...)` and
    # wraps execution in an escript; GDScript invokes Godot with a
    # driver script) can supply a custom handler here. Signature:
    #   (emitted, out_dir, meta, ctx) -> (stage, returncode, output)
    # where `ctx` is a dict with:
    #   "fuzz_workdir": Path — root of the fuzz run's bind mount
    #   "docker_exec":  Callable[[list[str], Path], list[str]]
    #                   — wraps a cmd to run via `docker exec` in the
    #                     lang's persistent container at the given host
    #                     working directory (which MUST be under
    #                     fuzz_workdir so it maps to /fuzz_work).
    # When set, the default compile/run path is bypassed entirely.
    run_custom: Optional[Callable[[Path, Path, dict, dict], tuple]] = None
    # Per-backend case filter. Returns True if the case described by
    # `meta` is runnable on this backend, False to skip (distinct from
    # pass/fail). Use for axis values the backend can't express — e.g.
    # Erlang's if/case syntax divergence makes the Phase-3 selfcall
    # `if_guarded` / `if_both_arms` post-structures infeasible until a
    # proper Erlang if-transform is built.
    # Default None: all cases supported.
    case_supported: Optional[Callable[[dict], bool]] = None
    # Maximum concurrent compile+run invocations of this backend under
    # the parallel case runner. Cap here for backends whose toolchain is
    # memory-heavy enough that saturating `--jobs` also saturates RAM.
    # Kotlin's `kotlinc -J-Xmx2g` × `--jobs` concurrency OOMs on a
    # 16-GB host; cap it to ~2. Default None = unbounded (subject only
    # to the overall `--jobs`).
    concurrency_limit: Optional[int] = None
    # Language support notes (free text, informational only).
    notes: str = ""


# --- Persist fuzz harness rendering helpers ---
#
# Each `renderers["persist"]` callback receives the case's meta dict from
# gen_persist_pure.py, which has:
#   sys_name         — "PersistNNNN"
#   axes             — n_states, hsm_depth, domain_set, target_offset
#   sequence         — advances_pre, set_x, set_s, set_b, expected_status
#
# The epilog drives: advance × advances_pre, set_x(int), set_s(str)
# and set_b(bool) if applicable, status() to capture, save, restore,
# then a second dump via get_x()/get_s()/get_b() + status() on the
# restored instance. Every backend must emit the same normalized trace.


def _fmt_bool_lit(lang_style: str, b: bool) -> str:
    """Native literal for a boolean in the given language family."""
    return {
        "py": "True" if b else "False",
        "lower": "true" if b else "false",
    }[lang_style]


def _norm_bool(expr: str, lang_style: str) -> str:
    """Expression that evaluates to `"true"` / `"false"` (lowercase) for
    a boolean value. Used in trace lines so every backend emits the same
    string regardless of native bool→string formatting."""
    return {
        "py": f"('true' if {expr} else 'false')",
    }[lang_style]


# --- Per-language canary harness rendering ---
#
# Each render function returns the epilog appended after the @@system
# block. The Frame source always declares `@@system Canary` with a
# single `go(): int` interface method that transitions A → B on first
# call and returns 9 forever on subsequent calls.


def py_canary(_: str) -> str:
    return """
if __name__ == '__main__':
    inst = @@Canary()
    print("TRACE: CALL go()")
    r = inst.go()
    print(f"TRACE: RET {r}")
    print("TRACE: CALL go()")
    r = inst.go()
    print(f"TRACE: RET {r}")
    blob = inst.save_state()
    print("TRACE: SAVE ok")
    inst2 = Canary.restore_state(blob)
    print("TRACE: RESTORE ok")
    print("TRACE: CALL go()")
    r = inst2.go()
    print(f"TRACE: RET {r}")
"""


def py_persist(meta: dict) -> str:
    """Python oracle for the persist fuzz. Every other backend's renderer
    must produce the exact same stdout bytes."""
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = ["", "if __name__ == '__main__':"]
    lines.append(f"    inst = @@{sys_name}()")
    for _ in range(advances_pre):
        lines.append("    inst.advance()")
        lines.append('    print("TRACE: advance")')
    lines.append(f"    inst.set_x({set_x})")
    lines.append(f'    print("TRACE: set_x {set_x}")')
    if has_str:
        lines.append(f'    inst.set_s("{set_s}")')
        lines.append(f'    print(\'TRACE: set_s "{set_s}"\')')
    if has_bool:
        lines.append(f"    inst.set_b({'True' if set_b else 'False'})")
        lines.append(f'    print("TRACE: set_b {"true" if set_b else "false"}")')
    lines.append('    print(f"TRACE: status {inst.status()}")')
    lines.append("    blob = inst.save_state()")
    lines.append('    print("TRACE: save ok")')
    lines.append(f"    rest = {sys_name}.restore_state(blob)")
    lines.append('    print("TRACE: restore ok")')
    lines.append('    print(f"TRACE: post_status {rest.status()}")')
    lines.append('    print(f"TRACE: post_x {rest.get_x()}")')
    if has_str:
        lines.append('    print(f\'TRACE: post_s "{rest.get_s()}"\')')
    if has_bool:
        # f-string can't contain a single-quoted literal inside its
        # braces, so we build the expression as a plain string.
        expr = "'true' if rest.get_b() else 'false'"
        lines.append(f'    print(f"TRACE: post_b {{{expr}}}")')
    lines.append('    print("TRACE: done")')
    return "\n".join(lines) + "\n"


# --- Phase-6 async fuzz harnesses ---
#
# Each renderer prepends a target-language async helper named `op` and
# appends a driver. The trace contract (every backend identical):
#
#   TRACE: CALL fetch
#   TRACE: RET <value>
#   TRACE: status <sN>
#
# Where <value> is the case's `expected.value` from gen_async_pure.py
# (e.g. "value_for_k" for single_await, "value_for_kvalue_for_k" for
# two_awaits) and <sN> is `expected.state`. Only Python is wired in
# initially; other 10 async backends (TS, JS, Rust, C++, C#, Java,
# Kotlin, Swift, Dart, GDScript) are TODO and would mirror the same
# `op` + driver shape in their respective async syntax.


def py_multisys(meta: dict) -> str:
    """Python oracle for the multi-system fuzz. Instantiates only
    the outer Driver — the inner Counter is constructed transitively
    via the outer's `domain:` initializer. Trace contract:

        TRACE: CALL run
        TRACE: CALL get_total
        TRACE: total <N>

    Where <N> is `expected.total`."""
    sys_name = meta["sys_name"]
    return f"""
if __name__ == '__main__':
    s = @@{sys_name}()
    print("TRACE: CALL run")
    s.run()
    print("TRACE: CALL get_total")
    print(f"TRACE: total {{s.get_total()}}")
"""


def ruby_multisys(meta: dict) -> str:
    """Ruby counterpart of `py_multisys`."""
    sys_name = meta["sys_name"]
    return f"""

s = {sys_name}.new
puts "TRACE: CALL run"
s.run
puts "TRACE: CALL get_total"
puts "TRACE: total #{{s.get_total}}"
"""


def lua_multisys(meta: dict) -> str:
    """Lua counterpart of `py_multisys`. Lua method dispatch is
    `:` (passes self). Frame's `self.inner.bump()` becomes
    `self:inner:bump()` in Lua — but that's already handled by
    `_lua_trace` for sync calls. Driver creates the outer with
    `:new()` and calls methods with `:`."""
    sys_name = meta["sys_name"]
    return f"""

local s = {sys_name}:new()
print("TRACE: CALL run")
s:run()
print("TRACE: CALL get_total")
print("TRACE: total " .. s:get_total())
"""


def php_multisys(meta: dict) -> str:
    """PHP counterpart of `py_multisys`."""
    sys_name = meta["sys_name"]
    return f"""

$s = new {sys_name}();
echo "TRACE: CALL run" . PHP_EOL;
$s->run();
echo "TRACE: CALL get_total" . PHP_EOL;
echo "TRACE: total " . $s->get_total() . PHP_EOL;
"""


def go_multisys(meta: dict) -> str:
    """Go counterpart of `py_multisys`. Note framec's Go backend
    uses `New<System>()` package-level constructor."""
    sys_name = meta["sys_name"]
    return f"""

func main() {{
    s := New{sys_name}()
    fmt.Println("TRACE: CALL run")
    s.Run()
    fmt.Println("TRACE: CALL get_total")
    fmt.Println("TRACE: total", s.GetTotal())
}}
"""


def py_async(meta: dict) -> str:
    """Python oracle for the async fuzz. The native helper `op` is the
    awaited callable that the generated handler body references; the
    driver runs the start-state cascade via `await s.init()` then
    invokes `s.fetch("k")` once and prints the trace.

    `asyncio.sleep(0)` inside `op` yields once to the event loop so
    the await is genuinely asynchronous (not a sync return)."""
    sys_name = meta["sys_name"]
    return f"""
import asyncio

async def op(key):
    await asyncio.sleep(0)
    return f"value_for_{{key}}"

async def main():
    s = @@{sys_name}()
    await s.init()
    print("TRACE: CALL fetch")
    r = await s.fetch("k")
    print(f"TRACE: RET {{r}}")
    print(f"TRACE: status {{await s.status()}}")

if __name__ == '__main__':
    asyncio.run(main())
"""


def js_multisys(meta: dict) -> str:
    """JS counterpart of `py_multisys`. The outer Driver constructs
    the inner Counter via its domain-init; the driver only news-up
    the Driver."""
    sys_name = meta["sys_name"]
    return f"""

const s = new {sys_name}();
console.log("TRACE: CALL run");
s.run();
console.log("TRACE: CALL get_total");
console.log(`TRACE: total ${{s.get_total()}}`);
"""


def js_async(meta: dict) -> str:
    """JS counterpart of `py_async`. Trace must byte-match the Python
    oracle. Node.js / ESM target — the runner uses `node --import .mjs`
    so top-level `await` is allowed."""
    sys_name = meta["sys_name"]
    return f"""

async function op(key) {{
    await Promise.resolve();
    return `value_for_${{key}}`;
}}

const s = new {sys_name}();
await s.init();
console.log("TRACE: CALL fetch");
const r = await s.fetch("k");
console.log(`TRACE: RET ${{r}}`);
console.log(`TRACE: status ${{await s.status()}}`);
"""


def ts_async(meta: dict) -> str:
    """TypeScript counterpart of `js_async`. The fuzz runner invokes
    `tsx` which compiles to CJS by default; CJS rejects top-level
    `await`, so the driver is wrapped in an immediately-invoked
    `async function main()`."""
    sys_name = meta["sys_name"]
    return f"""

async function op(key: string): Promise<string> {{
    await Promise.resolve();
    return `value_for_${{key}}`;
}}

async function main() {{
    const s = new {sys_name}();
    await s.init();
    console.log("TRACE: CALL fetch");
    const r = await s.fetch("k");
    console.log(`TRACE: RET ${{r}}`);
    console.log(`TRACE: status ${{await s.status()}}`);
}}

main();
"""


def rust_async(meta: dict) -> str:
    """Rust counterpart of `py_async`. Uses `futures::executor::block_on`
    instead of a full tokio runtime — the cases' awaited helper is
    trivially-resolvable, so a single-threaded poller suffices.

    `op` takes `&str` rather than `String` so the same parameter can
    be re-borrowed across multiple awaits in `two_awaits`. The
    `_rust_trace` rewriter inserts the `&` prefix on the call sites
    (Python-canonical `op(key)` → `op(&key).await`)."""
    sys_name = meta["sys_name"]
    return f"""

async fn op(key: &str) -> String {{
    format!("value_for_{{}}", key)
}}

fn main() {{
    futures::executor::block_on(async {{
        let mut s = {sys_name}::new();
        s.init().await;
        println!("TRACE: CALL fetch");
        let r = s.fetch(String::from("k")).await;
        println!("TRACE: RET {{}}", r);
        println!("TRACE: status {{}}", s.status().await);
    }});
}}
"""


def rust_multisys(meta: dict) -> str:
    """Rust counterpart of `py_multisys`. Inner Counter is held by
    value in the outer Driver's domain; framec emits a struct-init
    with `Counter::new()` for the `inner` field."""
    sys_name = meta["sys_name"]
    return f"""

fn main() {{
    let mut s = {sys_name}::new();
    println!("TRACE: CALL run");
    s.run();
    println!("TRACE: CALL get_total");
    println!("TRACE: total {{}}", s.get_total());
}}
"""


def rust_async_supported(meta: dict) -> bool:
    """Skip `two_awaits` on Rust. Frame's `@@:(self.tmp_a + self.tmp_b)`
    passes through to Rust verbatim, where `String + String` is a type
    error (Rust requires `String + &String`). Other backends accept
    the bare `+` for string concat. A target-aware rewrite of `+`
    inside `@@:(...)` is feasible but out of scope for Phase 6 first
    cut. Once that lands, drop this filter."""
    return meta.get("axes", {}).get("pattern") != "two_awaits"


def dart_multisys(meta: dict) -> str:
    """Dart counterpart of `py_multisys`. Top-level `void main()`."""
    sys_name = meta["sys_name"]
    return f"""

void main() {{
    final s = {sys_name}();
    print("TRACE: CALL run");
    s.run();
    print("TRACE: CALL get_total");
    print("TRACE: total " + s.get_total().toString());
}}
"""


def dart_async(meta: dict) -> str:
    """Dart counterpart of `py_async`. `dart compile kernel` with
    Dart's null-safety mode requires explicit types. `op` is a
    top-level `Future<String>` async function; main is
    `Future<void> main() async`."""
    sys_name = meta["sys_name"]
    return f"""

Future<String> op(String key) async {{
    return "value_for_" + key;
}}

Future<void> main() async {{
    final s = {sys_name}();
    await s.init();
    print("TRACE: CALL fetch");
    final r = await s.fetch("k");
    print("TRACE: RET " + r);
    print("TRACE: status " + (await s.status()));
}}
"""


def swift_async(meta: dict) -> str:
    """Swift counterpart of `py_async`. Swift uses native `async`/
    `await` (Swift 5.5+). The driver wraps in a `Task { ... }` and
    blocks via `DispatchSemaphore` so the script doesn't exit before
    awaits resolve. Swift's `init` is reserved for constructors;
    framec renames the API-parity helper to `initAsync` for Swift —
    see test_env demos/19_async_http_client.fswift."""
    sys_name = meta["sys_name"]
    return f"""

import Foundation

func op(_ key: String) async -> String {{
    return "value_for_" + key
}}

let __sem = DispatchSemaphore(value: 0)
Task {{
    let s = {sys_name}()
    await s.initAsync()
    print("TRACE: CALL fetch")
    let r = await s.fetch("k")
    print("TRACE: RET " + r)
    print("TRACE: status " + (await s.status()))
    __sem.signal()
}}
__sem.wait()
"""


def gdscript_multisys(meta: dict) -> str:
    """GDScript counterpart of `py_multisys`. Driver runs inside
    `SceneTree._init()` via the `extends SceneTree` prolog."""
    sys_name = meta["sys_name"]
    return f"""

func _init():
    var s = {sys_name}.new()
    print("TRACE: CALL run")
    s.run()
    print("TRACE: CALL get_total")
    print("TRACE: total " + str(s.get_total()))
    quit()
"""


def gdscript_async(meta: dict) -> str:
    """GDScript counterpart of `py_async`. Godot 4 supports native
    `await` (syntax matches Python). Driver runs inside
    `SceneTree._init()` which the `extends SceneTree` prolog
    already configures. `op` lives on a `Helpers` inner class as a
    static method — bare `op(...)` inside Async<NNNN> handler
    bodies doesn't resolve cross-class, so `_gdscript_trace`
    qualifies the call as `Helpers.op(...)`."""
    sys_name = meta["sys_name"]
    return f"""

class Helpers:
    static func op(key: String) -> String:
        return "value_for_" + key

func _init():
    var s = {sys_name}.new()
    await s.init()
    print("TRACE: CALL fetch")
    var r = await s.fetch("k")
    print("TRACE: RET " + r)
    print("TRACE: status " + await s.status())
    quit()
"""


def kotlin_async(meta: dict) -> str:
    """Kotlin counterpart of `py_async`. Kotlin uses `suspend fun`
    + `runBlocking { ... }` — `op` is a suspend function declared
    on a `Helpers` companion object, and `main()` opens a
    `runBlocking` block. `_kotlin_trace` drops the `await` keyword
    and qualifies `op(key)` as `Helpers.op(key)` since Kotlin's
    suspend calls don't need explicit await in a coroutine context.

    Kotlin imports must be at the top of the file but this renderer
    appends to the bottom; using the fully-qualified
    `kotlinx.coroutines.runBlocking` reference keeps the renderer
    self-contained without needing to wire a prolog."""
    sys_name = meta["sys_name"]
    return f"""

object Helpers {{
    suspend fun op(key: String): String {{
        return "value_for_" + key
    }}
}}

fun main() = kotlinx.coroutines.runBlocking {{
    val s = {sys_name}()
    s.init()
    println("TRACE: CALL fetch")
    val r = s.fetch("k")
    println("TRACE: RET " + r)
    println("TRACE: status " + s.status())
}}
"""


def java_multisys(meta: dict) -> str:
    """Java counterpart of `py_multisys`. Main lives on
    `<sys_name>Main` (matches the runner's `<stem>Main` convention)."""
    sys_name = meta["sys_name"]
    main_cls = f"{sys_name}Main"
    return f"""

class {main_cls} {{
    public static void main(String[] args) {{
        {sys_name} s = new {sys_name}();
        System.out.println("TRACE: CALL run");
        s.run();
        System.out.println("TRACE: CALL get_total");
        System.out.println("TRACE: total " + s.get_total());
    }}
}}
"""


def java_async(meta: dict) -> str:
    """Java counterpart of `py_async`. Java has no `async`/`await`
    keywords; framec lowers `async fetch(): String` to a method
    returning `CompletableFuture<String>` and leaves sync interface
    methods (`status(): str`) as plain returns. The driver `.join()`s
    each async call (unchecked-exception variant of `.get()`) and
    treats `status()` as a sync return.

    Java's runner naming convention: the file is `<sys_name>.java`
    and the main class is `<sys_name>Main` (the runner runs
    `java <stem>Main`). `op` lives on a separate `Helpers` static
    class so the in-handler `op(key)` reference (rewritten to
    `Helpers.op(key)` by `_java_trace`) is per-class-stable across
    cases."""
    sys_name = meta["sys_name"]
    main_cls = f"{sys_name}Main"
    return f"""

class Helpers {{
    public static java.util.concurrent.CompletableFuture<String> op(String key) {{
        return java.util.concurrent.CompletableFuture.completedFuture("value_for_" + key);
    }}
}}

class {main_cls} {{
    public static void main(String[] args) {{
        {sys_name} s = new {sys_name}();
        System.out.println("TRACE: CALL fetch");
        String r = s.fetch("k").join();
        System.out.println("TRACE: RET " + r);
        System.out.println("TRACE: status " + s.status());
    }}
}}
"""


def csharp_multisys(meta: dict) -> str:
    """C# counterpart of `py_multisys`. Driver lives on `CanaryMain`
    (csproj-hardcoded entry point)."""
    sys_name = meta["sys_name"]
    return f"""

public class CanaryMain {{
    public static void Main() {{
        var s = new {sys_name}();
        System.Console.WriteLine("TRACE: CALL run");
        s.run();
        System.Console.WriteLine("TRACE: CALL get_total");
        System.Console.WriteLine("TRACE: total " + s.get_total());
    }}
}}
"""


def csharp_async(meta: dict) -> str:
    """C# counterpart of `py_async`. The csproj hardcodes
    `<StartupObject>CanaryMain</StartupObject>`, so the entry point
    has to live on a class named `CanaryMain`. `op` lives on a
    `Helpers` companion class — bare `op(...)` calls inside handler
    bodies are rewritten to `Helpers.op(...)` by `_csharp_trace`,
    matching the same convention as Java."""
    sys_name = meta["sys_name"]
    return f"""

public static class Helpers {{
    public static async Task<string> op(string key) {{
        await Task.Yield();
        return "value_for_" + key;
    }}
}}

public class CanaryMain {{
    public static async Task Main() {{
        var s = new {sys_name}();
        await s.init();
        System.Console.WriteLine("TRACE: CALL fetch");
        var r = await s.fetch("k");
        System.Console.WriteLine("TRACE: RET " + r);
        System.Console.WriteLine("TRACE: status " + (await s.status()));
    }}
}}
"""


# --- Phase-3 @@:self fuzz harnesses ---
#
# Each renderer produces the same normalized trace against the oracle:
#   TRACE: drive
#   TRACE: status <sN>
#   TRACE: trace <int>
#   TRACE: done
#
# The per-backend variants differ only in native call syntax.


# Phase-9 nested-Frame-syntax fuzz renderers. Probe the system's
# `probe(x)` method and emit its return value. Minimal trace so the
# diff is stable across bool-rendering, stringification, and printf-
# formatting quirks — we keep the probe value integer-valued.


def py_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nif __name__ == '__main__':\n"
        f"    inst = @@{sys_name}()\n"
        f'    print(f"TRACE: probe {{inst.probe({x})}}")\n'
        f'    print("TRACE: done")\n'
    )


def js_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nconst inst = new {sys_name}();\n"
        f'console.log("TRACE: probe " + inst.probe({x}));\n'
        f'console.log("TRACE: done");\n'
    )


def ts_nested(meta: dict) -> str:
    return js_nested(meta)


def go_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nfunc main() {{\n"
        f"    inst := New{sys_name}()\n"
        f'    fmt.Printf("TRACE: probe %v\\n", inst.Probe({x}))\n'
        f'    fmt.Println("TRACE: done")\n'
        f"}}\n"
    )


def ruby_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\ninst = {sys_name}.new\n"
        f'puts "TRACE: probe #{{inst.probe({x})}}"\n'
        f'puts "TRACE: done"\n'
    )


def dart_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nvoid main() {{\n"
        f"    var inst = {sys_name}();\n"
        f'    print("TRACE: probe ${{inst.probe({x})}}");\n'
        f'    print("TRACE: done");\n'
        f"}}\n"
    )


def swift_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nlet inst = {sys_name}()\n"
        + r'print("TRACE: probe \(inst.probe('+str(x)+'))")' + "\n"
        + 'print("TRACE: done")\n'
    )


def csharp_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\npublic class CanaryMain {{\n"
        f"    public static void Main() {{\n"
        f"        var inst = new {sys_name}();\n"
        f'        System.Console.WriteLine("TRACE: probe " + inst.probe({x}));\n'
        f'        System.Console.WriteLine("TRACE: done");\n'
        f"    }}\n"
        f"}}\n"
    )


def rust_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nfn main() {{\n"
        f"    let mut inst = {sys_name}::new();\n"
        f'    println!("TRACE: probe {{}}", inst.probe({x}));\n'
        f'    println!("TRACE: done");\n'
        f"}}\n"
    )


def php_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\n$inst = new {sys_name}();\n"
        f'echo "TRACE: probe " . $inst->probe({x}) . PHP_EOL;\n'
        f'echo "TRACE: done" . PHP_EOL;\n'
    )


def java_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nclass {sys_name}Main {{\n"
        f"    public static void main(String[] args) {{\n"
        f"        {sys_name} inst = new {sys_name}();\n"
        f'        System.out.println("TRACE: probe " + inst.probe({x}));\n'
        f'        System.out.println("TRACE: done");\n'
        f"    }}\n"
        f"}}\n"
    )


def kotlin_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nfun main() {{\n"
        f"    val inst = {sys_name}()\n"
        f'    println("TRACE: probe ${{inst.probe({x})}}")\n'
        f'    println("TRACE: done")\n'
        f"}}\n"
    )


def cpp_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nint main() {{\n"
        f"    auto inst = {sys_name}();\n"
        f'    std::cout << "TRACE: probe " << inst.probe({x}) << std::endl;\n'
        f'    std::cout << "TRACE: done" << std::endl;\n'
        f"    return 0;\n"
        f"}}\n"
    )


def lua_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nlocal inst = {sys_name}:new()\n"
        f'print("TRACE: probe " .. tostring(inst:probe({x})))\n'
        f'print("TRACE: done")\n'
    )


def c_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nint main(void) {{\n"
        f"    {sys_name}* inst = @@{sys_name}();\n"
        f'    printf("TRACE: probe %d\\n", {sys_name}_probe(inst, {x}));\n'
        f'    printf("TRACE: done\\n");\n'
        f"    {sys_name}_destroy(inst);\n"
        f"    return 0;\n"
        f"}}\n"
    )


def gdscript_nested(meta: dict) -> str:
    sys_name = meta["sys_name"]
    x = meta["probe_x"]
    return (
        f"\nfunc _init():\n"
        f"    var inst = @@{sys_name}()\n"
        f'    print("TRACE: probe " + str(inst.probe({x})))\n'
        f'    print("TRACE: done")\n'
        f"    quit()\n"
    )


def _erlang_nested_escript(meta: dict) -> str:
    sys_name = meta["sys_name"]
    module = _erlang_module_name(sys_name)
    x = meta["probe_x"]
    return (
        "#!/usr/bin/env escript\n"
        "main(_) ->\n"
        '    code:add_patha("."),\n'
        f"    {{ok, Pid}} = {module}:start_link(),\n"
        f"    Result = {module}:probe(Pid, {x}),\n"
        '    io:format("TRACE: probe ~p~n", [Result]),\n'
        '    io:format("TRACE: done~n"),\n'
        "    init:stop().\n"
    )


def py_operations(meta: dict) -> str:
    """Python oracle for Phase-5 operations fuzz. Prints TRACE for:
      - direct op invocation (bypassing the state machine),
      - post-drive() result (op called via caller_context path),
      - final counter (to observe domain mutations).

    Python's `str(True)` is `"True"` but every other backend renders
    `true` lowercase. Frame has no cross-target bool-to-string rule,
    so we normalize here: any Python bool gets lowercased in-trace so
    byte-diff succeeds against JS/Go/etc."""
    sys_name = meta["sys_name"]
    return (
        f"\n_norm = lambda v: ('true' if v else 'false') if isinstance(v, bool) else v\n"
        f"if __name__ == '__main__':\n"
        f"    inst = @@{sys_name}()\n"
        f'    print(f"TRACE: direct {{_norm(inst.Op())}}")\n'
        f"    inst.drive()\n"
        f'    print(f"TRACE: via_event {{_norm(inst.get_result())}}")\n'
        f'    print(f"TRACE: counter {{inst.get_counter()}}")\n'
        f'    print("TRACE: done")\n'
    )


# Phase-5 operations fuzz renderers. Per-backend instantiates the
# system, calls op() directly (bypassing the state machine), fires
# drive() (which invokes op via the case's caller_context path),
# then prints direct/via_event/counter/done. Bool rendering is
# target-native where `tostring(bool)` already prints `"true"`/
# `"false"` (most backends); where it doesn't, an inline ternary
# produces the same string. `rtype` drives the print form — int
# and str use default stringification; bool uses the normalized
# form so the trace is byte-equal to Python's `_norm` oracle.


def _ops_rtype(meta: dict) -> str:
    return meta["axes"]["return_type"]


def js_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    rtype = _ops_rtype(meta)
    # JS `console.log(true)` → "true"; no normalization needed.
    _ = rtype  # type-driven variance not currently required
    return (
        f"\nconst inst = new {sys_name}();\n"
        f'console.log("TRACE: direct " + inst.Op());\n'
        f"inst.drive();\n"
        f'console.log("TRACE: via_event " + inst.get_result());\n'
        f'console.log("TRACE: counter " + inst.get_counter());\n'
        f'console.log("TRACE: done");\n'
    )


def ts_operations(meta: dict) -> str:
    # TypeScript uses the same runtime trace semantics as JS.
    return js_operations(meta)


def go_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    rtype = _ops_rtype(meta)
    # Go's fmt.Print on bool → "true"/"false"; on string → raw bytes;
    # on int → decimal. Default %v matches the oracle for every type.
    _ = rtype
    return (
        f"\nfunc main() {{\n"
        f"    inst := New{sys_name}()\n"
        f'    fmt.Printf("TRACE: direct %v\\n", inst.Op())\n'
        f"    inst.Drive()\n"
        f'    fmt.Printf("TRACE: via_event %v\\n", inst.Get_result())\n'
        f'    fmt.Printf("TRACE: counter %v\\n", inst.Get_counter())\n'
        f'    fmt.Println("TRACE: done")\n'
        f"}}\n"
    )


def ruby_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\ninst = {sys_name}.new\n"
        f'puts "TRACE: direct #{{inst.Op}}"\n'
        f"inst.drive\n"
        f'puts "TRACE: via_event #{{inst.get_result}}"\n'
        f'puts "TRACE: counter #{{inst.get_counter}}"\n'
        f'puts "TRACE: done"\n'
    )


def dart_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nvoid main() {{\n"
        f"    var inst = {sys_name}();\n"
        f'    print("TRACE: direct ${{inst.Op()}}");\n'
        f"    inst.drive();\n"
        f'    print("TRACE: via_event ${{inst.get_result()}}");\n'
        f'    print("TRACE: counter ${{inst.get_counter()}}");\n'
        f'    print("TRACE: done");\n'
        f"}}\n"
    )


def swift_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nlet inst = {sys_name}()\n"
        + r'print("TRACE: direct \(inst.Op())")' + "\n"
        f"inst.drive()\n"
        + r'print("TRACE: via_event \(inst.get_result())")' + "\n"
        + r'print("TRACE: counter \(inst.get_counter())")' + "\n"
        + 'print("TRACE: done")\n'
    )


def csharp_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    rtype = _ops_rtype(meta)
    # C#'s `object.ToString()` on bool yields "True"/"False" (capitalized).
    # Force lowercase explicitly when the op returns bool to match the
    # oracle.
    if rtype == "bool":
        fmt_direct = 'inst.Op().ToString().ToLower()'  # C# bool → "True"/"False" → normalize to lowercase
        fmt_via = 'inst.get_result().ToString().ToLower()'
    else:
        fmt_direct = 'inst.Op()'
        fmt_via = 'inst.get_result()'
    # Class name MUST be `CanaryMain` — the csproj hardcodes
    # `<StartupObject>CanaryMain</StartupObject>` (shared across all
    # harness kinds, including the persist/selfcall/hsm phases).
    return (
        f"\npublic class CanaryMain {{\n"
        f"    public static void Main() {{\n"
        f"        var inst = new {sys_name}();\n"
        f'        System.Console.WriteLine("TRACE: direct " + {fmt_direct});\n'
        f"        inst.drive();\n"
        f'        System.Console.WriteLine("TRACE: via_event " + {fmt_via});\n'
        f'        System.Console.WriteLine("TRACE: counter " + inst.get_counter());\n'
        f'        System.Console.WriteLine("TRACE: done");\n'
        f"    }}\n"
        f"}}\n"
    )


def rust_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nfn main() {{\n"
        f"    let mut inst = {sys_name}::new();\n"
        f'    println!("TRACE: direct {{}}", inst.Op());\n'
        f"    inst.drive();\n"
        f'    println!("TRACE: via_event {{}}", inst.get_result());\n'
        f'    println!("TRACE: counter {{}}", inst.get_counter());\n'
        f'    println!("TRACE: done");\n'
        f"}}\n"
    )


def php_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    rtype = _ops_rtype(meta)
    # PHP echoes bool false as `""` and true as `"1"` — neither matches
    # the oracle. Use var_export for bool; regular echo for int/str.
    if rtype == "bool":
        fmt_direct = 'var_export($inst->Op(), true)'
        fmt_via = 'var_export($inst->get_result(), true)'
    else:
        fmt_direct = '$inst->Op()'
        fmt_via = '$inst->get_result()'
    return (
        f"\n$inst = new {sys_name}();\n"
        f'echo "TRACE: direct " . {fmt_direct} . PHP_EOL;\n'
        f"$inst->drive();\n"
        f'echo "TRACE: via_event " . {fmt_via} . PHP_EOL;\n'
        f'echo "TRACE: counter " . $inst->get_counter() . PHP_EOL;\n'
        f'echo "TRACE: done" . PHP_EOL;\n'
    )


def java_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nclass {sys_name}Main {{\n"
        f"    public static void main(String[] args) {{\n"
        f"        {sys_name} inst = new {sys_name}();\n"
        f'        System.out.println("TRACE: direct " + inst.Op());\n'
        f"        inst.drive();\n"
        f'        System.out.println("TRACE: via_event " + inst.get_result());\n'
        f'        System.out.println("TRACE: counter " + inst.get_counter());\n'
        f'        System.out.println("TRACE: done");\n'
        f"    }}\n"
        f"}}\n"
    )


def kotlin_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nfun main() {{\n"
        f"    val inst = {sys_name}()\n"
        f'    println("TRACE: direct ${{inst.Op()}}")\n'
        f"    inst.drive()\n"
        f'    println("TRACE: via_event ${{inst.get_result()}}")\n'
        f'    println("TRACE: counter ${{inst.get_counter()}}")\n'
        f'    println("TRACE: done")\n'
        f"}}\n"
    )


def cpp_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    rtype = _ops_rtype(meta)
    # C++ default stream << bool prints 1/0. Enable boolalpha globally
    # so bool renders "true"/"false" matching the oracle. For str/int
    # the flag is a no-op.
    _ = rtype
    return (
        f"\nint main() {{\n"
        f"    std::cout << std::boolalpha;\n"
        f"    auto inst = {sys_name}();\n"
        f'    std::cout << "TRACE: direct " << inst.Op() << std::endl;\n'
        f"    inst.drive();\n"
        f'    std::cout << "TRACE: via_event " << inst.get_result() << std::endl;\n'
        f'    std::cout << "TRACE: counter " << inst.get_counter() << std::endl;\n'
        f'    std::cout << "TRACE: done" << std::endl;\n'
        f"    return 0;\n"
        f"}}\n"
    )


def lua_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    rtype = _ops_rtype(meta)
    # Lua's tostring(true) → "true"; string.format "%s" with bool
    # errors out. Use tostring() consistently.
    _ = rtype
    return (
        f"\nlocal inst = {sys_name}:new()\n"
        f'print("TRACE: direct " .. tostring(inst:Op()))\n'
        f"inst:drive()\n"
        f'print("TRACE: via_event " .. tostring(inst:get_result()))\n'
        f'print("TRACE: counter " .. tostring(inst:get_counter()))\n'
        f'print("TRACE: done")\n'
    )


def c_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    rtype = _ops_rtype(meta)
    # framec's C backend emits functions prefixed with the capital
    # `<SysName>_<method>` and a `<SysName>_new()` constructor that
    # returns a heap-allocated pointer. `@@SysName()` is Frame sugar
    # that framec expands to `<SysName>_new()`. Bool in C is `int`
    # (0/1) so we ternary-render for trace parity with the oracle.
    if rtype == "bool":
        direct = f'({sys_name}_Op(inst) ? "true" : "false")'
        via = f'({sys_name}_get_result(inst) ? "true" : "false")'
        direct_fmt = '%s'
        via_fmt = '%s'
    elif rtype == "str":
        direct = f'{sys_name}_Op(inst)'
        via = f'{sys_name}_get_result(inst)'
        direct_fmt = '%s'
        via_fmt = '%s'
    else:  # int
        direct = f'{sys_name}_Op(inst)'
        via = f'{sys_name}_get_result(inst)'
        direct_fmt = '%d'
        via_fmt = '%d'
    return (
        f"\nint main(void) {{\n"
        f"    {sys_name}* inst = @@{sys_name}();\n"
        f'    printf("TRACE: direct {direct_fmt}\\n", {direct});\n'
        f"    {sys_name}_drive(inst);\n"
        f'    printf("TRACE: via_event {via_fmt}\\n", {via});\n'
        f'    printf("TRACE: counter %d\\n", {sys_name}_get_counter(inst));\n'
        f'    printf("TRACE: done\\n");\n'
        f"    {sys_name}_destroy(inst);\n"
        f"    return 0;\n"
        f"}}\n"
    )


def gdscript_operations(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nfunc _init():\n"
        f"    var inst = @@{sys_name}()\n"
        f'    print("TRACE: direct " + str(inst.Op()))\n'
        f"    inst.drive()\n"
        f'    print("TRACE: via_event " + str(inst.get_result()))\n'
        f'    print("TRACE: counter " + str(inst.get_counter()))\n'
        f'    print("TRACE: done")\n'
        f"    quit()\n"
    )


def _erlang_operations_escript(meta: dict) -> str:
    sys_name = meta["sys_name"]
    module = _erlang_module_name(sys_name)
    rtype = _ops_rtype(meta)
    # Erlang atoms `true`/`false` already render lowercase via ~p. For
    # str rtype, the op returns an Erlang string (list of chars); use
    # ~s to emit the raw chars. For int, ~p. For bool, ~p → `true`/
    # `false`.
    if rtype == "str":
        fmt = "~s"
    else:
        fmt = "~p"
    return (
        "#!/usr/bin/env escript\n"
        "main(_) ->\n"
        '    code:add_patha("."),\n'
        f"    {{ok, Pid}} = {module}:start_link(),\n"
        f"    Direct = {module}:op(Pid),\n"
        f'    io:format("TRACE: direct {fmt}~n", [Direct]),\n'
        f"    _ = {module}:drive(Pid),\n"
        f"    ViaEvent = {module}:get_result(Pid),\n"
        f'    io:format("TRACE: via_event {fmt}~n", [ViaEvent]),\n'
        f"    Counter = {module}:get_counter(Pid),\n"
        '    io:format("TRACE: counter ~p~n", [Counter]),\n'
        '    io:format("TRACE: done~n"),\n'
        "    init:stop().\n"
    )


def py_selfcall(meta: dict) -> str:
    """Python oracle — canonical trace output."""
    sys_name = meta["sys_name"]
    return (
        f"\nif __name__ == '__main__':\n"
        f"    inst = @@{sys_name}()\n"
        f"    inst.drive()\n"
        f'    print("TRACE: drive")\n'
        f'    print(f"TRACE: status {{inst.status()}}")\n'
        f'    print(f"TRACE: trace {{inst.trace()}}")\n'
        f'    print("TRACE: done")\n'
    )


def js_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nconst inst = new {sys_name}();\n"
        f"inst.drive();\n"
        f'console.log("TRACE: drive");\n'
        f'console.log("TRACE: status " + inst.status());\n'
        f'console.log("TRACE: trace " + inst.trace());\n'
        f'console.log("TRACE: done");\n'
    )


def ruby_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\ninst = {sys_name}.new\n"
        f"inst.drive\n"
        f'puts "TRACE: drive"\n'
        f'puts "TRACE: status #{{inst.status}}"\n'
        f'puts "TRACE: trace #{{inst.trace}}"\n'
        f'puts "TRACE: done"\n'
    )


def go_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nfunc main() {{\n"
        f"    inst := New{sys_name}()\n"
        f"    inst.Drive()\n"
        f'    fmt.Println("TRACE: drive")\n'
        f'    fmt.Printf("TRACE: status %s\\n", inst.Status())\n'
        f'    fmt.Printf("TRACE: trace %d\\n", inst.Trace())\n'
        f'    fmt.Println("TRACE: done")\n'
        f"}}\n"
    )


def dart_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nvoid main() {{\n"
        f"    var inst = {sys_name}();\n"
        f"    inst.drive();\n"
        f'    print("TRACE: drive");\n'
        f'    print("TRACE: status ${{inst.status()}}");\n'
        f'    print("TRACE: trace ${{inst.trace()}}");\n'
        f'    print("TRACE: done");\n'
        f"}}\n"
    )


def swift_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nlet inst = {sys_name}()\n"
        f"inst.drive()\n"
        f'print("TRACE: drive")\n'
        r'print("TRACE: status \(inst.status())")' "\n"
        r'print("TRACE: trace \(inst.trace())")' "\n"
        f'print("TRACE: done")\n'
    )


def csharp_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\npublic class CanaryMain {{\n"
        f"    public static void Main() {{\n"
        f"        var inst = new {sys_name}();\n"
        f"        inst.drive();\n"
        f'        System.Console.WriteLine("TRACE: drive");\n'
        f'        System.Console.WriteLine("TRACE: status " + inst.status());\n'
        f'        System.Console.WriteLine("TRACE: trace " + inst.trace());\n'
        f'        System.Console.WriteLine("TRACE: done");\n'
        f"    }}\n"
        f"}}\n"
    )


def rust_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nfn main() {{\n"
        f"    let mut inst = {sys_name}::new();\n"
        f"    inst.drive();\n"
        f'    println!("TRACE: drive");\n'
        f'    println!("TRACE: status {{}}", inst.status());\n'
        f'    println!("TRACE: trace {{}}", inst.trace());\n'
        f'    println!("TRACE: done");\n'
        f"}}\n"
    )


def php_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\n$inst = new {sys_name}();\n"
        f"$inst->drive();\n"
        f'echo "TRACE: drive" . PHP_EOL;\n'
        f'echo "TRACE: status " . $inst->status() . PHP_EOL;\n'
        f'echo "TRACE: trace " . $inst->trace() . PHP_EOL;\n'
        f'echo "TRACE: done" . PHP_EOL;\n'
    )


def java_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nclass {sys_name}Main {{\n"
        f"    public static void main(String[] args) {{\n"
        f"        {sys_name} inst = new {sys_name}();\n"
        f"        inst.drive();\n"
        f'        System.out.println("TRACE: drive");\n'
        f'        System.out.println("TRACE: status " + inst.status());\n'
        f'        System.out.println("TRACE: trace " + inst.trace());\n'
        f'        System.out.println("TRACE: done");\n'
        f"    }}\n"
        f"}}\n"
    )


def kotlin_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nfun main() {{\n"
        f"    val inst = {sys_name}()\n"
        f"    inst.drive()\n"
        f'    println("TRACE: drive")\n'
        f'    println("TRACE: status ${{inst.status()}}")\n'
        f'    println("TRACE: trace ${{inst.trace()}}")\n'
        f'    println("TRACE: done")\n'
        f"}}\n"
    )


def cpp_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nint main() {{\n"
        f"    {sys_name} inst;\n"
        f"    inst.drive();\n"
        f'    std::cout << "TRACE: drive" << std::endl;\n'
        f'    std::cout << "TRACE: status " << std::any_cast<std::string>(inst.status()) << std::endl;\n'
        f'    std::cout << "TRACE: trace " << std::any_cast<int>(inst.trace()) << std::endl;\n'
        f'    std::cout << "TRACE: done" << std::endl;\n'
        f"    return 0;\n"
        f"}}\n"
    )


def lua_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nlocal inst = {sys_name}:new()\n"
        f"inst:drive()\n"
        f'print("TRACE: drive")\n'
        f'print("TRACE: status " .. inst:status())\n'
        f'print("TRACE: trace " .. string.format("%d", inst:trace()))\n'
        f'print("TRACE: done")\n'
    )


def c_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nint main(void) {{\n"
        f"    {sys_name}* inst = @@{sys_name}();\n"
        f"    {sys_name}_drive(inst);\n"
        f'    printf("TRACE: drive\\n");\n'
        f'    printf("TRACE: status %s\\n", {sys_name}_status(inst));\n'
        f'    printf("TRACE: trace %d\\n", {sys_name}_trace(inst));\n'
        f'    printf("TRACE: done\\n");\n'
        f"    {sys_name}_destroy(inst);\n"
        f"    return 0;\n"
        f"}}\n"
    )


def gdscript_selfcall(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nfunc _init():\n"
        f"    var inst = @@{sys_name}()\n"
        f"    inst.drive()\n"
        f'    print("TRACE: drive")\n'
        f'    print("TRACE: status " + str(inst.status()))\n'
        f'    print("TRACE: trace " + str(inst.trace()))\n'
        f'    print("TRACE: done")\n'
        f"    quit()\n"
    )


def _erlang_selfcall_escript(meta: dict) -> str:
    """Escript driver for @@:self fuzz — emitted by erlang_run_custom
    when `meta["harness_kind"] == "selfcall"`."""
    sys_name = meta["sys_name"]
    module = _erlang_module_name(sys_name)
    return (
        "#!/usr/bin/env escript\n"
        "main(_) ->\n"
        '    code:add_patha("."),\n'
        f"    {{ok, Pid}} = {module}:start_link(),\n"
        f"    _ = {module}:drive(Pid),\n"
        '    io:format("TRACE: drive~n"),\n'
        f"    Status = {module}:status(Pid),\n"
        '    io:format("TRACE: status ~s~n", [Status]),\n'
        f"    Trace = {module}:trace(Pid),\n"
        '    io:format("TRACE: trace ~p~n", [Trace]),\n'
        '    io:format("TRACE: done~n"),\n'
        "    init:stop().\n"
    )


# --- Phase 4: HSM parent-semantics renderers ---
#
# Identical to the selfcall renderers plus one extra TRACE line for
# `parent_count()` so the fuzz asserts that the parent's handler ran
# the expected number of times across the `=> $^` event-forward. The
# child caller's interface is still `drive()`; observation methods
# are `status()`, `trace()`, `parent_count()`.


def py_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nif __name__ == '__main__':\n"
        f"    inst = @@{sys_name}()\n"
        f"    inst.drive()\n"
        f'    print("TRACE: drive")\n'
        f'    print(f"TRACE: status {{inst.status()}}")\n'
        f'    print(f"TRACE: trace {{inst.trace()}}")\n'
        f'    print(f"TRACE: parent_count {{inst.parent_count()}}")\n'
        f'    print("TRACE: done")\n'
    )


def js_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nconst inst = new {sys_name}();\n"
        f"inst.drive();\n"
        f'console.log("TRACE: drive");\n'
        f'console.log("TRACE: status " + inst.status());\n'
        f'console.log("TRACE: trace " + inst.trace());\n'
        f'console.log("TRACE: parent_count " + inst.parent_count());\n'
        f'console.log("TRACE: done");\n'
    )


def ruby_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\ninst = {sys_name}.new\n"
        f"inst.drive\n"
        f'puts "TRACE: drive"\n'
        f'puts "TRACE: status #{{inst.status}}"\n'
        f'puts "TRACE: trace #{{inst.trace}}"\n'
        f'puts "TRACE: parent_count #{{inst.parent_count}}"\n'
        f'puts "TRACE: done"\n'
    )


def go_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nfunc main() {{\n"
        f"    inst := New{sys_name}()\n"
        f"    inst.Drive()\n"
        f'    fmt.Println("TRACE: drive")\n'
        f'    fmt.Printf("TRACE: status %s\\n", inst.Status())\n'
        f'    fmt.Printf("TRACE: trace %d\\n", inst.Trace())\n'
        f'    fmt.Printf("TRACE: parent_count %d\\n", inst.Parent_count())\n'
        f'    fmt.Println("TRACE: done")\n'
        f"}}\n"
    )


def dart_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nvoid main() {{\n"
        f"    var inst = {sys_name}();\n"
        f"    inst.drive();\n"
        f'    print("TRACE: drive");\n'
        f'    print("TRACE: status ${{inst.status()}}");\n'
        f'    print("TRACE: trace ${{inst.trace()}}");\n'
        f'    print("TRACE: parent_count ${{inst.parent_count()}}");\n'
        f'    print("TRACE: done");\n'
        f"}}\n"
    )


def swift_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nlet inst = {sys_name}()\n"
        f"inst.drive()\n"
        f'print("TRACE: drive")\n'
        r'print("TRACE: status \(inst.status())")' "\n"
        r'print("TRACE: trace \(inst.trace())")' "\n"
        r'print("TRACE: parent_count \(inst.parent_count())")' "\n"
        f'print("TRACE: done")\n'
    )


def csharp_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\npublic class CanaryMain {{\n"
        f"    public static void Main() {{\n"
        f"        var inst = new {sys_name}();\n"
        f"        inst.drive();\n"
        f'        System.Console.WriteLine("TRACE: drive");\n'
        f'        System.Console.WriteLine("TRACE: status " + inst.status());\n'
        f'        System.Console.WriteLine("TRACE: trace " + inst.trace());\n'
        f'        System.Console.WriteLine("TRACE: parent_count " + inst.parent_count());\n'
        f'        System.Console.WriteLine("TRACE: done");\n'
        f"    }}\n"
        f"}}\n"
    )


def rust_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nfn main() {{\n"
        f"    let mut inst = {sys_name}::new();\n"
        f"    inst.drive();\n"
        f'    println!("TRACE: drive");\n'
        f'    println!("TRACE: status {{}}", inst.status());\n'
        f'    println!("TRACE: trace {{}}", inst.trace());\n'
        f'    println!("TRACE: parent_count {{}}", inst.parent_count());\n'
        f'    println!("TRACE: done");\n'
        f"}}\n"
    )


def php_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\n$inst = new {sys_name}();\n"
        f"$inst->drive();\n"
        f'echo "TRACE: drive" . PHP_EOL;\n'
        f'echo "TRACE: status " . $inst->status() . PHP_EOL;\n'
        f'echo "TRACE: trace " . $inst->trace() . PHP_EOL;\n'
        f'echo "TRACE: parent_count " . $inst->parent_count() . PHP_EOL;\n'
        f'echo "TRACE: done" . PHP_EOL;\n'
    )


def java_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nclass {sys_name}Main {{\n"
        f"    public static void main(String[] args) {{\n"
        f"        {sys_name} inst = new {sys_name}();\n"
        f"        inst.drive();\n"
        f'        System.out.println("TRACE: drive");\n'
        f'        System.out.println("TRACE: status " + inst.status());\n'
        f'        System.out.println("TRACE: trace " + inst.trace());\n'
        f'        System.out.println("TRACE: parent_count " + inst.parent_count());\n'
        f'        System.out.println("TRACE: done");\n'
        f"    }}\n"
        f"}}\n"
    )


def kotlin_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nfun main() {{\n"
        f"    val inst = {sys_name}()\n"
        f"    inst.drive()\n"
        f'    println("TRACE: drive")\n'
        f'    println("TRACE: status ${{inst.status()}}")\n'
        f'    println("TRACE: trace ${{inst.trace()}}")\n'
        f'    println("TRACE: parent_count ${{inst.parent_count()}}")\n'
        f'    println("TRACE: done")\n'
        f"}}\n"
    )


def cpp_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nint main() {{\n"
        f"    {sys_name} inst;\n"
        f"    inst.drive();\n"
        f'    std::cout << "TRACE: drive" << std::endl;\n'
        f'    std::cout << "TRACE: status " << std::any_cast<std::string>(inst.status()) << std::endl;\n'
        f'    std::cout << "TRACE: trace " << std::any_cast<int>(inst.trace()) << std::endl;\n'
        f'    std::cout << "TRACE: parent_count " << std::any_cast<int>(inst.parent_count()) << std::endl;\n'
        f'    std::cout << "TRACE: done" << std::endl;\n'
        f"    return 0;\n"
        f"}}\n"
    )


def lua_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nlocal inst = {sys_name}:new()\n"
        f"inst:drive()\n"
        f'print("TRACE: drive")\n'
        f'print("TRACE: status " .. inst:status())\n'
        f'print("TRACE: trace " .. string.format("%d", inst:trace()))\n'
        f'print("TRACE: parent_count " .. string.format("%d", inst:parent_count()))\n'
        f'print("TRACE: done")\n'
    )


def c_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nint main(void) {{\n"
        f"    {sys_name}* inst = @@{sys_name}();\n"
        f"    {sys_name}_drive(inst);\n"
        f'    printf("TRACE: drive\\n");\n'
        f'    printf("TRACE: status %s\\n", {sys_name}_status(inst));\n'
        f'    printf("TRACE: trace %d\\n", {sys_name}_trace(inst));\n'
        f'    printf("TRACE: parent_count %d\\n", {sys_name}_parent_count(inst));\n'
        f'    printf("TRACE: done\\n");\n'
        f"    {sys_name}_destroy(inst);\n"
        f"    return 0;\n"
        f"}}\n"
    )


def gdscript_hsm(meta: dict) -> str:
    sys_name = meta["sys_name"]
    return (
        f"\nfunc _init():\n"
        f"    var inst = @@{sys_name}()\n"
        f"    inst.drive()\n"
        f'    print("TRACE: drive")\n'
        f'    print("TRACE: status " + str(inst.status()))\n'
        f'    print("TRACE: trace " + str(inst.trace()))\n'
        f'    print("TRACE: parent_count " + str(inst.parent_count()))\n'
        f'    print("TRACE: done")\n'
        f"    quit()\n"
    )


def _erlang_hsm_escript(meta: dict) -> str:
    """Escript driver for HSM parent-semantics fuzz — emitted by
    `erlang_run_custom` when `meta["harness_kind"] == "hsm"`."""
    sys_name = meta["sys_name"]
    module = _erlang_module_name(sys_name)
    return (
        "#!/usr/bin/env escript\n"
        "main(_) ->\n"
        '    code:add_patha("."),\n'
        f"    {{ok, Pid}} = {module}:start_link(),\n"
        f"    _ = {module}:drive(Pid),\n"
        '    io:format("TRACE: drive~n"),\n'
        f"    Status = {module}:status(Pid),\n"
        '    io:format("TRACE: status ~s~n", [Status]),\n'
        f"    Trace = {module}:trace(Pid),\n"
        '    io:format("TRACE: trace ~p~n", [Trace]),\n'
        f"    Pc = {module}:parent_count(Pid),\n"
        '    io:format("TRACE: parent_count ~p~n", [Pc]),\n'
        '    io:format("TRACE: done~n"),\n'
        "    init:stop().\n"
    )


def js_canary(_: str) -> str:
    return """
const inst = new Canary();
console.log("TRACE: CALL go()");
let r = inst.go();
console.log("TRACE: RET " + r);
console.log("TRACE: CALL go()");
r = inst.go();
console.log("TRACE: RET " + r);
const blob = inst.saveState();
console.log("TRACE: SAVE ok");
const inst2 = Canary.restoreState(blob);
console.log("TRACE: RESTORE ok");
console.log("TRACE: CALL go()");
r = inst2.go();
console.log("TRACE: RET " + r);
"""


def js_persist(meta: dict) -> str:
    """JS persist harness — must produce byte-identical trace to py_persist."""
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = [""]
    lines.append(f"const inst = new {sys_name}();")
    for _ in range(advances_pre):
        lines.append("inst.advance();")
        lines.append('console.log("TRACE: advance");')
    lines.append(f"inst.set_x({set_x});")
    lines.append(f'console.log("TRACE: set_x {set_x}");')
    if has_str:
        lines.append(f'inst.set_s("{set_s}");')
        lines.append(f'console.log(\'TRACE: set_s "{set_s}"\');')
    if has_bool:
        lines.append(f"inst.set_b({'true' if set_b else 'false'});")
        lines.append(f'console.log("TRACE: set_b {"true" if set_b else "false"}");')
    lines.append('console.log("TRACE: status " + inst.status());')
    lines.append("const blob = inst.saveState();")
    lines.append('console.log("TRACE: save ok");')
    lines.append(f"const rest = {sys_name}.restoreState(blob);")
    lines.append('console.log("TRACE: restore ok");')
    lines.append('console.log("TRACE: post_status " + rest.status());')
    lines.append('console.log("TRACE: post_x " + rest.get_x());')
    if has_str:
        lines.append('console.log(\'TRACE: post_s "\' + rest.get_s() + \'"\');')
    if has_bool:
        lines.append(
            'console.log("TRACE: post_b " + (rest.get_b() ? "true" : "false"));'
        )
    lines.append('console.log("TRACE: done");')
    return "\n".join(lines) + "\n"


def ts_canary(_: str) -> str:
    return """
const inst = new Canary();
console.log("TRACE: CALL go()");
let r = inst.go();
console.log("TRACE: RET " + r);
console.log("TRACE: CALL go()");
r = inst.go();
console.log("TRACE: RET " + r);
const blob = inst.saveState();
console.log("TRACE: SAVE ok");
const inst2 = Canary.restoreState(blob);
console.log("TRACE: RESTORE ok");
console.log("TRACE: CALL go()");
r = inst2.go();
console.log("TRACE: RET " + r);
"""


# --- Per-language canary harnesses (continued) ---


def go_persist(meta: dict) -> str:
    """Go harness. Framec emits methods as `FirstUpper + rest unchanged`,
    so `set_x` → `Set_x`. Auto-generated persist methods use PascalCase
    (`SaveState`). Restore is package-level: `RestorePersistNNNN(blob)`."""
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = ["", "func main() {"]
    lines.append(f"    inst := New{sys_name}()")
    for _ in range(advances_pre):
        lines.append("    inst.Advance()")
        lines.append('    fmt.Println("TRACE: advance")')
    lines.append(f"    inst.Set_x({set_x})")
    lines.append(f'    fmt.Println("TRACE: set_x {set_x}")')
    if has_str:
        lines.append(f'    inst.Set_s("{set_s}")')
        lines.append(f'    fmt.Printf("TRACE: set_s \\"{set_s}\\"\\n")')
    if has_bool:
        lines.append(f"    inst.Set_b({'true' if set_b else 'false'})")
        lines.append(f'    fmt.Println("TRACE: set_b {"true" if set_b else "false"}")')
    lines.append('    fmt.Printf("TRACE: status %s\\n", inst.Status())')
    lines.append("    blob := inst.SaveState()")
    lines.append('    fmt.Println("TRACE: save ok")')
    lines.append(f"    rest := Restore{sys_name}(blob)")
    lines.append('    fmt.Println("TRACE: restore ok")')
    lines.append('    fmt.Printf("TRACE: post_status %s\\n", rest.Status())')
    lines.append('    fmt.Printf("TRACE: post_x %d\\n", rest.Get_x())')
    if has_str:
        lines.append('    fmt.Printf("TRACE: post_s \\"%s\\"\\n", rest.Get_s())')
    if has_bool:
        lines.append('    b_str := "false"')
        lines.append('    if rest.Get_b() { b_str = "true" }')
        lines.append('    fmt.Printf("TRACE: post_b %s\\n", b_str)')
    lines.append('    fmt.Println("TRACE: done")')
    lines.append("}")
    return "\n".join(lines) + "\n"


def ruby_persist(meta: dict) -> str:
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = [""]
    lines.append(f"inst = {sys_name}.new")
    for _ in range(advances_pre):
        lines.append("inst.advance")
        lines.append('puts "TRACE: advance"')
    lines.append(f"inst.set_x({set_x})")
    lines.append(f'puts "TRACE: set_x {set_x}"')
    if has_str:
        lines.append(f'inst.set_s("{set_s}")')
        lines.append(f'puts \'TRACE: set_s "{set_s}"\'')
    if has_bool:
        lines.append(f"inst.set_b({'true' if set_b else 'false'})")
        lines.append(f'puts "TRACE: set_b {"true" if set_b else "false"}"')
    lines.append('puts "TRACE: status #{inst.status}"')
    lines.append("blob = inst.save_state")
    lines.append('puts "TRACE: save ok"')
    lines.append(f"rest = {sys_name}.restore_state(blob)")
    lines.append('puts "TRACE: restore ok"')
    lines.append('puts "TRACE: post_status #{rest.status}"')
    lines.append('puts "TRACE: post_x #{rest.get_x}"')
    if has_str:
        lines.append('puts \'TRACE: post_s "\' + rest.get_s + \'"\'')
    if has_bool:
        lines.append('puts "TRACE: post_b #{rest.get_b ? \'true\' : \'false\'}"')
    lines.append('puts "TRACE: done"')
    return "\n".join(lines) + "\n"


def go_canary(_: str) -> str:
    # Go uses uppercase method names (exported); restore is package-level.
    return """
func main() {
    inst := NewCanary()
    fmt.Println("TRACE: CALL go()")
    r := inst.Go()
    fmt.Printf("TRACE: RET %d\\n", r)
    fmt.Println("TRACE: CALL go()")
    r = inst.Go()
    fmt.Printf("TRACE: RET %d\\n", r)
    blob := inst.SaveState()
    fmt.Println("TRACE: SAVE ok")
    inst2 := RestoreCanary(blob)
    fmt.Println("TRACE: RESTORE ok")
    fmt.Println("TRACE: CALL go()")
    r = inst2.Go()
    fmt.Printf("TRACE: RET %d\\n", r)
}
"""


def ruby_canary(_: str) -> str:
    return """
inst = Canary.new
puts "TRACE: CALL go()"
r = inst.go
puts "TRACE: RET #{r}"
puts "TRACE: CALL go()"
r = inst.go
puts "TRACE: RET #{r}"
blob = inst.save_state
puts "TRACE: SAVE ok"
inst2 = Canary.restore_state(blob)
puts "TRACE: RESTORE ok"
puts "TRACE: CALL go()"
r = inst2.go
puts "TRACE: RET #{r}"
"""


def php_canary(_: str) -> str:
    # No leading `<?php` — prolog already supplies it.
    return """
$inst = new Canary();
echo "TRACE: CALL go()\\n";
$r = $inst->go();
echo "TRACE: RET $r\\n";
echo "TRACE: CALL go()\\n";
$r = $inst->go();
echo "TRACE: RET $r\\n";
$blob = $inst->save_state();
echo "TRACE: SAVE ok\\n";
$inst2 = Canary::restore_state($blob);
echo "TRACE: RESTORE ok\\n";
echo "TRACE: CALL go()\\n";
$r = $inst2->go();
echo "TRACE: RET $r\\n";
"""


def dart_canary(_: str) -> str:
    return """
void main() {
    var inst = Canary();
    print("TRACE: CALL go()");
    var r = inst.go();
    print("TRACE: RET $r");
    print("TRACE: CALL go()");
    r = inst.go();
    print("TRACE: RET $r");
    var blob = inst.saveState();
    print("TRACE: SAVE ok");
    var inst2 = Canary.restoreState(blob);
    print("TRACE: RESTORE ok");
    print("TRACE: CALL go()");
    r = inst2.go();
    print("TRACE: RET $r");
}
"""


def php_persist(meta: dict) -> str:
    """PHP persist harness. Uses `<?php ... ?>` prolog, `Class::method()`
    for static calls, `$inst->method()` for instance calls. The body
    constructs its own trace via `echo ... . PHP_EOL;`."""
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = [""]
    lines.append(f"$inst = new {sys_name}();")
    for _ in range(advances_pre):
        lines.append("$inst->advance();")
        lines.append('echo "TRACE: advance" . PHP_EOL;')
    lines.append(f"$inst->set_x({set_x});")
    lines.append(f'echo "TRACE: set_x {set_x}" . PHP_EOL;')
    if has_str:
        lines.append(f'$inst->set_s("{set_s}");')
        lines.append(f'echo "TRACE: set_s \\"{set_s}\\"" . PHP_EOL;')
    if has_bool:
        lines.append(f"$inst->set_b({'true' if set_b else 'false'});")
        lines.append(f'echo "TRACE: set_b {"true" if set_b else "false"}" . PHP_EOL;')
    lines.append('echo "TRACE: status " . $inst->status() . PHP_EOL;')
    lines.append("$blob = $inst->save_state();")
    lines.append('echo "TRACE: save ok" . PHP_EOL;')
    lines.append(f"$rest = {sys_name}::restore_state($blob);")
    lines.append('echo "TRACE: restore ok" . PHP_EOL;')
    lines.append('echo "TRACE: post_status " . $rest->status() . PHP_EOL;')
    lines.append('echo "TRACE: post_x " . $rest->get_x() . PHP_EOL;')
    if has_str:
        lines.append('echo \'TRACE: post_s "\' . $rest->get_s() . \'"\' . PHP_EOL;')
    if has_bool:
        lines.append(
            'echo "TRACE: post_b " . ($rest->get_b() ? "true" : "false") . PHP_EOL;'
        )
    lines.append('echo "TRACE: done" . PHP_EOL;')
    return "\n".join(lines) + "\n"


def dart_persist(meta: dict) -> str:
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = ["", "void main() {"]
    lines.append(f"    var inst = {sys_name}();")
    for _ in range(advances_pre):
        lines.append("    inst.advance();")
        lines.append('    print("TRACE: advance");')
    lines.append(f"    inst.set_x({set_x});")
    lines.append(f'    print("TRACE: set_x {set_x}");')
    if has_str:
        lines.append(f'    inst.set_s("{set_s}");')
        lines.append(f'    print(\'TRACE: set_s "{set_s}"\');')
    if has_bool:
        lines.append(f"    inst.set_b({'true' if set_b else 'false'});")
        lines.append(f'    print("TRACE: set_b {"true" if set_b else "false"}");')
    # Dart interpolates `$foo` — escape literal `$` unused here; method
    # calls go in `${expr}`.
    lines.append('    print("TRACE: status ${inst.status()}");')
    lines.append("    var blob = inst.saveState();")
    lines.append('    print("TRACE: save ok");')
    lines.append(f"    var rest = {sys_name}.restoreState(blob);")
    lines.append('    print("TRACE: restore ok");')
    lines.append('    print("TRACE: post_status ${rest.status()}");')
    lines.append('    print("TRACE: post_x ${rest.get_x()}");')
    if has_str:
        lines.append('    print(\'TRACE: post_s "\' + rest.get_s() + \'"\');')
    if has_bool:
        lines.append('    print("TRACE: post_b ${rest.get_b() ? \'true\' : \'false\'}");')
    lines.append('    print("TRACE: done");')
    lines.append("}")
    return "\n".join(lines) + "\n"


def swift_persist(meta: dict) -> str:
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = [""]
    lines.append(f"let inst = {sys_name}()")
    for _ in range(advances_pre):
        lines.append("inst.advance()")
        lines.append('print("TRACE: advance")')
    lines.append(f"inst.set_x({set_x})")
    lines.append(f'print("TRACE: set_x {set_x}")')
    if has_str:
        lines.append(f'inst.set_s("{set_s}")')
        lines.append(f'print("TRACE: set_s \\"{set_s}\\"")')
    if has_bool:
        lines.append(f"inst.set_b({'true' if set_b else 'false'})")
        lines.append(f'print("TRACE: set_b {"true" if set_b else "false"}")')
    # Swift interpolation: \(expr)
    lines.append(r'print("TRACE: status \(inst.status())")')
    lines.append("let blob = inst.saveState()")
    lines.append('print("TRACE: save ok")')
    lines.append(f"let rest = {sys_name}.restoreState(blob)")
    lines.append('print("TRACE: restore ok")')
    lines.append(r'print("TRACE: post_status \(rest.status())")')
    lines.append(r'print("TRACE: post_x \(rest.get_x())")')
    if has_str:
        lines.append(r'print("TRACE: post_s \"\(rest.get_s())\"")')
    if has_bool:
        lines.append(
            r'print("TRACE: post_b \(rest.get_b() ? "true" : "false")")'
        )
    lines.append('print("TRACE: done")')
    return "\n".join(lines) + "\n"


def java_persist(meta: dict) -> str:
    """Java persist harness. framec emits `<SysName>.java` with the
    system class; we append a `<SysName>Main` class with `main()`. All
    trace output goes through `System.out.println` — wrapped in one
    method for brevity."""
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = ["", f"class {sys_name}Main {{"]
    lines.append("    public static void main(String[] args) {")
    lines.append(f"        {sys_name} inst = new {sys_name}();")
    for _ in range(advances_pre):
        lines.append("        inst.advance();")
        lines.append('        System.out.println("TRACE: advance");')
    lines.append(f"        inst.set_x({set_x});")
    lines.append(f'        System.out.println("TRACE: set_x {set_x}");')
    if has_str:
        lines.append(f'        inst.set_s("{set_s}");')
        lines.append(f'        System.out.println("TRACE: set_s \\"{set_s}\\"");')
    if has_bool:
        lines.append(f"        inst.set_b({'true' if set_b else 'false'});")
        lines.append(f'        System.out.println("TRACE: set_b {"true" if set_b else "false"}");')
    lines.append('        System.out.println("TRACE: status " + inst.status());')
    lines.append("        String blob = inst.save_state();")
    lines.append('        System.out.println("TRACE: save ok");')
    lines.append(f"        {sys_name} rest = {sys_name}.restore_state(blob);")
    lines.append('        System.out.println("TRACE: restore ok");')
    lines.append('        System.out.println("TRACE: post_status " + rest.status());')
    lines.append('        System.out.println("TRACE: post_x " + rest.get_x());')
    if has_str:
        lines.append(
            '        System.out.println("TRACE: post_s \\"" + rest.get_s() + "\\"");'
        )
    if has_bool:
        lines.append(
            '        System.out.println("TRACE: post_b " + ((boolean)rest.get_b() ? "true" : "false"));'
        )
    lines.append('        System.out.println("TRACE: done");')
    lines.append("    }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def java_canary(_: str) -> str:
    return """
class CanaryMain {
    public static void main(String[] args) {
        Canary inst = new Canary();
        System.out.println("TRACE: CALL go()");
        long r = inst.go();
        System.out.println("TRACE: RET " + r);
        System.out.println("TRACE: CALL go()");
        r = inst.go();
        System.out.println("TRACE: RET " + r);
        String blob = inst.save_state();
        System.out.println("TRACE: SAVE ok");
        Canary inst2 = Canary.restore_state(blob);
        System.out.println("TRACE: RESTORE ok");
        System.out.println("TRACE: CALL go()");
        r = inst2.go();
        System.out.println("TRACE: RET " + r);
    }
}
"""


def kotlin_canary(_: str) -> str:
    return """
fun main() {
    val inst = Canary()
    println("TRACE: CALL go()")
    var r = inst.go()
    println("TRACE: RET $r")
    println("TRACE: CALL go()")
    r = inst.go()
    println("TRACE: RET $r")
    val blob = inst.save_state()
    println("TRACE: SAVE ok")
    val inst2 = Canary.restore_state(blob)
    println("TRACE: RESTORE ok")
    println("TRACE: CALL go()")
    r = inst2.go()
    println("TRACE: RET $r")
}
"""


def swift_canary(_: str) -> str:
    return """
let inst = Canary()
print("TRACE: CALL go()")
var r = inst.go()
print("TRACE: RET \\(r)")
print("TRACE: CALL go()")
r = inst.go()
print("TRACE: RET \\(r)")
let blob = inst.saveState()
print("TRACE: SAVE ok")
let inst2 = Canary.restoreState(blob)
print("TRACE: RESTORE ok")
print("TRACE: CALL go()")
r = inst2.go()
print("TRACE: RET \\(r)")
"""


def c_persist(meta: dict) -> str:
    """C persist harness. framec emits a single .c file with a struct
    type and `SysName_method(self, args)` functions. `@@SysName()`
    expands to `SysName_new()`; persist API is
    `SysName_save_state(self) → char*` and
    `SysName_restore_state(json) → SysName*`."""
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = ["", "int main(void) {"]
    lines.append(f"    {sys_name}* inst = @@{sys_name}();")
    for _ in range(advances_pre):
        lines.append(f"    {sys_name}_advance(inst);")
        lines.append('    printf("TRACE: advance\\n");')
    lines.append(f"    {sys_name}_set_x(inst, {set_x});")
    lines.append(f'    printf("TRACE: set_x {set_x}\\n");')
    if has_str:
        lines.append(f'    {sys_name}_set_s(inst, "{set_s}");')
        lines.append(f'    printf("TRACE: set_s \\"{set_s}\\"\\n");')
    if has_bool:
        # C's bool literal in stdbool.h is lowercase `true`/`false`.
        lines.append(f"    {sys_name}_set_b(inst, {'true' if set_b else 'false'});")
        lines.append(f'    printf("TRACE: set_b {"true" if set_b else "false"}\\n");')
    lines.append(f'    printf("TRACE: status %s\\n", {sys_name}_status(inst));')
    lines.append(f"    char* blob = {sys_name}_save_state(inst);")
    lines.append('    printf("TRACE: save ok\\n");')
    lines.append(f"    {sys_name}* rest = {sys_name}_restore_state(blob);")
    lines.append('    printf("TRACE: restore ok\\n");')
    lines.append(f'    printf("TRACE: post_status %s\\n", {sys_name}_status(rest));')
    lines.append(f'    printf("TRACE: post_x %d\\n", {sys_name}_get_x(rest));')
    if has_str:
        lines.append(
            f'    printf("TRACE: post_s \\"%s\\"\\n", {sys_name}_get_s(rest));'
        )
    if has_bool:
        lines.append(
            f'    printf("TRACE: post_b %s\\n", {sys_name}_get_b(rest) ? "true" : "false");'
        )
    lines.append('    printf("TRACE: done\\n");')
    lines.append(f"    {sys_name}_destroy(inst);")
    lines.append(f"    {sys_name}_destroy(rest);")
    lines.append("    free(blob);")
    lines.append("    return 0;")
    lines.append("}")
    return "\n".join(lines) + "\n"


def csharp_persist(meta: dict) -> str:
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = ["", "public class CanaryMain {"]
    lines.append("    public static void Main() {")
    lines.append(f"        var inst = new {sys_name}();")
    for _ in range(advances_pre):
        lines.append("        inst.advance();")
        lines.append('        System.Console.WriteLine("TRACE: advance");')
    lines.append(f"        inst.set_x({set_x});")
    lines.append(f'        System.Console.WriteLine("TRACE: set_x {set_x}");')
    if has_str:
        lines.append(f'        inst.set_s("{set_s}");')
        lines.append(f'        System.Console.WriteLine("TRACE: set_s \\"{set_s}\\"");')
    if has_bool:
        lines.append(f"        inst.set_b({'true' if set_b else 'false'});")
        lines.append(f'        System.Console.WriteLine("TRACE: set_b {"true" if set_b else "false"}");')
    lines.append('        System.Console.WriteLine("TRACE: status " + inst.status());')
    lines.append("        var blob = inst.SaveState();")
    lines.append('        System.Console.WriteLine("TRACE: save ok");')
    lines.append(f"        var rest = {sys_name}.RestoreState(blob);")
    lines.append('        System.Console.WriteLine("TRACE: restore ok");')
    lines.append('        System.Console.WriteLine("TRACE: post_status " + rest.status());')
    lines.append('        System.Console.WriteLine("TRACE: post_x " + rest.get_x());')
    if has_str:
        lines.append(
            '        System.Console.WriteLine("TRACE: post_s \\"" + rest.get_s() + "\\"");'
        )
    if has_bool:
        lines.append(
            '        System.Console.WriteLine("TRACE: post_b " + (((bool)rest.get_b()) ? "true" : "false"));'
        )
    lines.append('        System.Console.WriteLine("TRACE: done");')
    lines.append("    }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def kotlin_persist(meta: dict) -> str:
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = ["", "fun main() {"]
    lines.append(f"    val inst = {sys_name}()")
    for _ in range(advances_pre):
        lines.append("    inst.advance()")
        lines.append('    println("TRACE: advance")')
    lines.append(f"    inst.set_x({set_x})")
    lines.append(f'    println("TRACE: set_x {set_x}")')
    if has_str:
        lines.append(f'    inst.set_s("{set_s}")')
        lines.append(f'    println("TRACE: set_s \\"{set_s}\\"")')
    if has_bool:
        lines.append(f"    inst.set_b({'true' if set_b else 'false'})")
        lines.append(f'    println("TRACE: set_b {"true" if set_b else "false"}")')
    lines.append('    println("TRACE: status ${inst.status()}")')
    lines.append("    val blob = inst.save_state()")
    lines.append('    println("TRACE: save ok")')
    # framec's Kotlin codegen now emits `restore_state` inside the
    # `companion object { }` block so it's callable statically,
    # matching every other backend's persist API.
    lines.append(f"    val rest = {sys_name}.restore_state(blob)")
    lines.append('    println("TRACE: restore ok")')
    lines.append('    println("TRACE: post_status ${rest.status()}")')
    lines.append('    println("TRACE: post_x ${rest.get_x()}")')
    if has_str:
        lines.append('    println("TRACE: post_s \\"${rest.get_s()}\\"")')
    if has_bool:
        # Avoid nested-quote escapes inside the string interpolation
        # brace — Kotlin's parser handles the escapes inconsistently.
        # A named local binds cleanly.
        lines.append('    val __b_str = if (rest.get_b() as Boolean) "true" else "false"')
        lines.append('    println("TRACE: post_b $__b_str")')
    lines.append('    println("TRACE: done")')
    lines.append("}")
    return "\n".join(lines) + "\n"


def rust_persist(meta: dict) -> str:
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = ["", "fn main() {"]
    lines.append(f"    let mut inst = {sys_name}::new();")
    for _ in range(advances_pre):
        lines.append("    inst.advance();")
        lines.append('    println!("TRACE: advance");')
    lines.append(f"    inst.set_x({set_x});")
    lines.append(f'    println!("TRACE: set_x {set_x}");')
    if has_str:
        lines.append(f'    inst.set_s(String::from("{set_s}"));')
        lines.append(f'    println!("TRACE: set_s \\"{set_s}\\"");')
    if has_bool:
        lines.append(f"    inst.set_b({'true' if set_b else 'false'});")
        lines.append(f'    println!("TRACE: set_b {"true" if set_b else "false"}");')
    lines.append('    println!("TRACE: status {}", inst.status());')
    lines.append("    let blob = inst.save_state();")
    lines.append('    println!("TRACE: save ok");')
    lines.append(f"    let mut rest = {sys_name}::restore_state(&blob);")
    lines.append('    println!("TRACE: restore ok");')
    lines.append('    println!("TRACE: post_status {}", rest.status());')
    lines.append('    println!("TRACE: post_x {}", rest.get_x());')
    if has_str:
        lines.append(r'    println!("TRACE: post_s \"{}\"", rest.get_s());')
    if has_bool:
        lines.append(
            '    println!("TRACE: post_b {}", if rest.get_b() { "true" } else { "false" });'
        )
    lines.append('    println!("TRACE: done");')
    lines.append("}")
    return "\n".join(lines) + "\n"


def lua_persist(meta: dict) -> str:
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = [""]
    lines.append(f"local inst = {sys_name}:new()")
    for _ in range(advances_pre):
        lines.append("inst:advance()")
        lines.append('print("TRACE: advance")')
    lines.append(f"inst:set_x({set_x})")
    lines.append(f'print("TRACE: set_x {set_x}")')
    if has_str:
        lines.append(f'inst:set_s("{set_s}")')
        lines.append(f'print(\'TRACE: set_s "{set_s}"\')')
    if has_bool:
        lines.append(f"inst:set_b({'true' if set_b else 'false'})")
        lines.append(f'print("TRACE: set_b {"true" if set_b else "false"}")')
    lines.append('print("TRACE: status " .. inst:status())')
    lines.append("local blob = inst:save_state()")
    lines.append('print("TRACE: save ok")')
    lines.append(f"local rest = {sys_name}.restore_state(blob)")
    lines.append('print("TRACE: restore ok")')
    lines.append('print("TRACE: post_status " .. rest:status())')
    # Lua's cjson decodes `x` as a float on round-trip, so `1000`
    # comes back as `1000.0`. Force integer formatting to match the
    # Python oracle's stringified int.
    lines.append('print("TRACE: post_x " .. string.format("%d", rest:get_x()))')
    if has_str:
        lines.append('print(\'TRACE: post_s "\' .. rest:get_s() .. \'"\')')
    if has_bool:
        # Lua: no ternary; use and/or idiom.
        lines.append(
            "print(\"TRACE: post_b \" .. (rest:get_b() and \"true\" or \"false\"))"
        )
    lines.append('print("TRACE: done")')
    return "\n".join(lines) + "\n"


def gdscript_persist(meta: dict) -> str:
    """GDScript persist harness. Runs as a Godot --headless --script.
    Entry point is `func _init()` in a `SceneTree`-extending class."""
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = ["", "func _init():"]
    lines.append(f"    var inst = @@{sys_name}()")
    for _ in range(advances_pre):
        lines.append("    inst.advance()")
        lines.append('    print("TRACE: advance")')
    lines.append(f"    inst.set_x({set_x})")
    lines.append(f'    print("TRACE: set_x {set_x}")')
    if has_str:
        lines.append(f'    inst.set_s("{set_s}")')
        lines.append(f'    print(\'TRACE: set_s "{set_s}"\')')
    if has_bool:
        lines.append(f"    inst.set_b({'true' if set_b else 'false'})")
        lines.append(f'    print("TRACE: set_b {"true" if set_b else "false"}")')
    lines.append('    print("TRACE: status " + str(inst.status()))')
    lines.append("    var blob = inst.save_state()")
    lines.append('    print("TRACE: save ok")')
    lines.append(f"    var rest = {sys_name}.restore_state(blob)")
    lines.append('    print("TRACE: restore ok")')
    lines.append('    print("TRACE: post_status " + str(rest.status()))')
    lines.append('    print("TRACE: post_x " + str(rest.get_x()))')
    if has_str:
        lines.append('    print(\'TRACE: post_s "\' + str(rest.get_s()) + \'"\')')
    if has_bool:
        lines.append(
            '    print("TRACE: post_b " + ("true" if rest.get_b() else "false"))'
        )
    lines.append('    print("TRACE: done")')
    lines.append("    quit()")
    return "\n".join(lines) + "\n"


def gdscript_run_custom(emitted: Path, out_dir: Path, meta: dict, ctx: dict) -> tuple:
    """Run the emitted .gd through Godot headless inside the
    docker-gdscript container. Uses the persistent container pool
    (via `ctx["docker_exec"]`) so each case is a `docker exec`, not a
    new container.

    Godot prints "Godot Engine vX.Y ..." on startup which we filter
    out of stdout — the oracle trace doesn't include it."""
    import subprocess
    cmd = ctx["docker_exec"](
        ["godot", "--headless", "--script", emitted.name],
        out_dir,
    )
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return ("run", 124, "run timed out")
    # Strip the engine banner from the output so the diff against the
    # Python oracle only sees the TRACE lines.
    filtered = "\n".join(
        l for l in proc.stdout.splitlines()
        if not l.startswith("Godot Engine")
    )
    return ("run", proc.returncode, filtered if proc.returncode == 0 else filtered + proc.stderr)


def _erlang_module_name(sys_name: str) -> str:
    """Convert a Frame system name (PascalCase) to its Erlang module
    name (snake_case). Mirrors `to_snake_case` in framec's codegen."""
    out = []
    for i, c in enumerate(sys_name):
        if c.isupper() and i > 0 and not sys_name[i - 1].isupper():
            out.append('_')
        out.append(c.lower())
    return ''.join(out)


def _erlang_persist_escript(meta: dict) -> str:
    """Return the escript driver text that runs the persist sequence
    against the compiled Erlang module. Called by `erlang_run_custom`
    after the module compiles."""
    sys_name = meta["sys_name"]
    module = _erlang_module_name(sys_name)
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = ["#!/usr/bin/env escript"]
    lines.append("main(_) ->")
    lines.append('    code:add_patha("."),')
    lines.append(f"    {{ok, Pid}} = {module}:start_link(),")
    for _ in range(advances_pre):
        lines.append(f"    _ = {module}:advance(Pid),")
        lines.append('    io:format("TRACE: advance~n"),')
    lines.append(f"    _ = {module}:set_x(Pid, {set_x}),")
    lines.append(f'    io:format("TRACE: set_x {set_x}~n"),')
    if has_str:
        lines.append(f'    _ = {module}:set_s(Pid, "{set_s}"),')
        lines.append(f'    io:format("TRACE: set_s \\"{set_s}\\"~n"),')
    if has_bool:
        lines.append(f"    _ = {module}:set_b(Pid, {'true' if set_b else 'false'}),")
        lines.append(f'    io:format("TRACE: set_b {"true" if set_b else "false"}~n"),')
    lines.append(f"    Status = {module}:status(Pid),")
    lines.append('    io:format("TRACE: status ~s~n", [Status]),')
    lines.append(f"    Blob = {module}:save_state(Pid),")
    lines.append('    io:format("TRACE: save ok~n"),')
    lines.append(f"    {{ok, Pid2}} = {module}:load_state(Blob),")
    lines.append('    io:format("TRACE: restore ok~n"),')
    lines.append(f"    PostStatus = {module}:status(Pid2),")
    lines.append('    io:format("TRACE: post_status ~s~n", [PostStatus]),')
    lines.append(f"    PostX = {module}:get_x(Pid2),")
    lines.append('    io:format("TRACE: post_x ~p~n", [PostX]),')
    if has_str:
        lines.append(f"    PostS = {module}:get_s(Pid2),")
        lines.append('    io:format("TRACE: post_s \\"~s\\"~n", [PostS]),')
    if has_bool:
        lines.append(f"    PostB = {module}:get_b(Pid2),")
        lines.append('    BStr = case PostB of true -> "true"; _ -> "false" end,')
        lines.append('    io:format("TRACE: post_b ~s~n", [BStr]),')
    lines.append('    io:format("TRACE: done~n"),')
    lines.append("    init:stop().")
    return "\n".join(lines) + "\n"


_ERLANG_ESCRIPT_BY_KIND = {
    "persist": lambda meta: _erlang_persist_escript(meta),
    "selfcall": lambda meta: _erlang_selfcall_escript(meta),
    "hsm": lambda meta: _erlang_hsm_escript(meta),
    "operations": lambda meta: _erlang_operations_escript(meta),
    "nested": lambda meta: _erlang_nested_escript(meta),
}


def erlang_case_supported(meta: dict) -> bool:
    """Historically Erlang was gated to `linear` post-structures
    because Python-indent `if X:` / `else:` passed through framec
    unchanged, yielding a parse error. With `_py_if_to_c_family`
    now active in `_erlang_trace` (2026-04-24), the canonical
    Python-style source is pre-converted to brace form before framec
    sees it, and `erlang_transform_blocks` converts brace-if to
    `case/of/end`. All post-structures are supported."""
    _ = meta
    return True


def erlang_run_custom(emitted: Path, out_dir: Path, meta: dict, ctx: dict) -> tuple:
    """End-to-end Erlang compile + run via the persistent-container
    pool:
      1. Rename the emitted `.erl` to `<module>.erl` so erlc is happy.
      2. `docker exec … erlc …` → `<module>.beam`.
      3. Write the escript driver built from `meta` (selected by
         `meta["harness_kind"]`).
      4. `docker exec … escript …` to run it.
    Returns `(stage, returncode, output)`."""
    import subprocess
    sys_name = meta["sys_name"]
    module = _erlang_module_name(sys_name)
    target_erl = out_dir / f"{module}.erl"
    # Step 1: rename.
    if emitted != target_erl:
        emitted.rename(target_erl)
    # Step 2: compile via the persistent container (`docker exec`).
    compile_cmd = ctx["docker_exec"](["erlc", f"{module}.erl"], out_dir)
    proc = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=180)
    if proc.returncode != 0:
        return ("compile", proc.returncode, proc.stdout + proc.stderr)
    # Step 3: pick the escript driver for this case's kind and write it.
    kind = meta.get("harness_kind", "persist")
    driver_fn = _ERLANG_ESCRIPT_BY_KIND.get(kind)
    if driver_fn is None:
        return ("compile", 1, f"erlang: no escript template for kind {kind!r}")
    driver = out_dir / "run_test.escript"
    driver.write_text(driver_fn(meta))
    driver.chmod(0o755)
    # Step 4: execute.
    run_cmd = ctx["docker_exec"](["escript", "run_test.escript"], out_dir)
    try:
        proc = subprocess.run(run_cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return ("run", 124, "run timed out")
    return ("run", proc.returncode, proc.stdout if proc.returncode == 0 else proc.stdout + proc.stderr)


def cpp_persist(meta: dict) -> str:
    """C++ persist harness. framec targets C++23; the generated system
    is a class with static save_state/restore_state."""
    sys_name = meta["sys_name"]
    seq = meta["sequence"]
    advances_pre = seq["advances_pre"]
    set_x = seq["set_x"]
    set_s = seq["set_s"]
    set_b = seq["set_b"]
    has_str = set_s is not None
    has_bool = set_b is not None

    lines = ["", "int main() {"]
    lines.append(f"    {sys_name} inst;")
    for _ in range(advances_pre):
        lines.append("    inst.advance();")
        lines.append('    std::cout << "TRACE: advance" << std::endl;')
    lines.append(f"    inst.set_x({set_x});")
    lines.append(f'    std::cout << "TRACE: set_x {set_x}" << std::endl;')
    if has_str:
        lines.append(f'    inst.set_s(std::string("{set_s}"));')
        lines.append(f'    std::cout << "TRACE: set_s \\"{set_s}\\"" << std::endl;')
    if has_bool:
        lines.append(f"    inst.set_b({'true' if set_b else 'false'});")
        lines.append(f'    std::cout << "TRACE: set_b {"true" if set_b else "false"}" << std::endl;')
    lines.append(
        '    std::cout << "TRACE: status " << std::any_cast<std::string>(inst.status()) << std::endl;'
    )
    lines.append("    std::string blob = inst.save_state();")
    lines.append('    std::cout << "TRACE: save ok" << std::endl;')
    lines.append(f"    {sys_name} rest = {sys_name}::restore_state(blob);")
    lines.append('    std::cout << "TRACE: restore ok" << std::endl;')
    lines.append(
        '    std::cout << "TRACE: post_status " << std::any_cast<std::string>(rest.status()) << std::endl;'
    )
    lines.append(
        '    std::cout << "TRACE: post_x " << std::any_cast<int>(rest.get_x()) << std::endl;'
    )
    if has_str:
        lines.append(
            '    std::cout << "TRACE: post_s \\"" << std::any_cast<std::string>(rest.get_s()) << "\\"" << std::endl;'
        )
    if has_bool:
        lines.append(
            '    std::cout << "TRACE: post_b " << (std::any_cast<bool>(rest.get_b()) ? "true" : "false") << std::endl;'
        )
    lines.append('    std::cout << "TRACE: done" << std::endl;')
    lines.append("    return 0;")
    lines.append("}")
    return "\n".join(lines) + "\n"


def cpp_canary(_: str) -> str:
    return """
int main() {
    Canary inst;
    std::cout << "TRACE: CALL go()" << std::endl;
    long r = inst.go();
    std::cout << "TRACE: RET " << r << std::endl;
    std::cout << "TRACE: CALL go()" << std::endl;
    r = inst.go();
    std::cout << "TRACE: RET " << r << std::endl;
    std::string blob = inst.save_state();
    std::cout << "TRACE: SAVE ok" << std::endl;
    Canary inst2 = Canary::restore_state(blob);
    std::cout << "TRACE: RESTORE ok" << std::endl;
    std::cout << "TRACE: CALL go()" << std::endl;
    r = inst2.go();
    std::cout << "TRACE: RET " << r << std::endl;
    return 0;
}
"""


def csharp_canary(_: str) -> str:
    return """
public class CanaryMain {
    public static void Main() {
        var inst = new Canary();
        System.Console.WriteLine("TRACE: CALL go()");
        long r = inst.go();
        System.Console.WriteLine("TRACE: RET " + r);
        System.Console.WriteLine("TRACE: CALL go()");
        r = inst.go();
        System.Console.WriteLine("TRACE: RET " + r);
        string blob = inst.SaveState();
        System.Console.WriteLine("TRACE: SAVE ok");
        Canary inst2 = Canary.RestoreState(blob);
        System.Console.WriteLine("TRACE: RESTORE ok");
        System.Console.WriteLine("TRACE: CALL go()");
        r = inst2.go();
        System.Console.WriteLine("TRACE: RET " + r);
    }
}
"""


def rust_canary(_: str) -> str:
    # framec Rust emits `pub fn go(&mut self) -> i32 { … }` on the
    # System struct. `save_state(&mut self) -> String`,
    # `restore_state(json: String) -> Self`.
    return """
fn main() {
    let mut inst = Canary::new();
    println!("TRACE: CALL go()");
    let r = inst.go();
    println!("TRACE: RET {}", r);
    println!("TRACE: CALL go()");
    let r = inst.go();
    println!("TRACE: RET {}", r);
    let blob = inst.save_state();
    println!("TRACE: SAVE ok");
    let mut inst2 = Canary::restore_state(&blob);
    println!("TRACE: RESTORE ok");
    println!("TRACE: CALL go()");
    let r = inst2.go();
    println!("TRACE: RET {}", r);
}
"""


def lua_canary(_: str) -> str:
    return """
local inst = Canary:new()
print("TRACE: CALL go()")
local r = inst:go()
print("TRACE: RET " .. r)
print("TRACE: CALL go()")
r = inst:go()
print("TRACE: RET " .. r)
local blob = inst:save_state()
print("TRACE: SAVE ok")
local inst2 = Canary.restore_state(blob)
print("TRACE: RESTORE ok")
print("TRACE: CALL go()")
r = inst2:go()
print("TRACE: RET " .. r)
"""


# --- Compile and run helpers ---


def run_python(p: Path) -> List[str]:
    return ["python3", str(p)]


def run_node_esm(p: Path) -> List[str]:
    # node requires `.mjs` for ESM; callers copy the .js to .mjs before running.
    mjs = p.with_suffix(".mjs")
    if not mjs.exists():
        mjs.write_bytes(p.read_bytes())
    return ["node", str(mjs)]


def run_ts(p: Path) -> List[str]:
    # ts-node or ts runner; for now use tsx if available, else bun.
    return ["npx", "tsx", str(p)]


def run_go(p: Path) -> List[str]:
    return ["go", "run", str(p)]


def run_ruby(p: Path) -> List[str]:
    return ["ruby", str(p)]


def run_lua(p: Path) -> List[str]:
    # Inside docker-lua the binary is `lua5.4`. On the host we fall
    # back to `lua` if 5.4 isn't on PATH (fuzz for Lua is docker-backed
    # because the cjson dependency isn't typically installed on macOS).
    # The runner passes a BARE filename (relative to the container's
    # cwd) when `lang.docker_image` is set, so we can't look for a
    # `/work/` prefix anymore — detect docker-mode by absence of a
    # parent path component.
    in_container = p.parent == Path('') or str(p) == p.name
    if in_container or _which("lua5.4"):
        return ["lua5.4", str(p)]
    return ["lua", str(p)]


def run_php(p: Path) -> List[str]:
    return ["php", str(p)]


def run_dart(p: Path) -> List[str]:
    return ["dart", "run", str(p)]


def compile_c(p: Path) -> List[str]:
    # docker-c image ships cJSON in /usr/include/cjson and linker
    # finds it via `-lcjson`. The emitted .c file is self-contained.
    bin_path = p.with_suffix("")
    return ["gcc", "-o", str(bin_path), str(p), "-lcjson"]


def run_c(p: Path) -> List[str]:
    # Executable invocation must be path-qualified (shell won't search
    # PATH for a bare name). When given a bare filename (inside the
    # docker pool's cwd), prefix `./` to run from cwd; absolute paths
    # pass through unchanged (host mode).
    bin_path = p.with_suffix("")
    bin_str = str(bin_path)
    if bin_path.is_absolute():
        return [bin_str]
    return [f"./{bin_str}"]


def compile_java(p: Path) -> List[str]:
    # Frame emits the class under an exact filename; javac produces .class.
    # In docker-java the container ships org.json at /lib/json.jar, so
    # include it on the classpath for the persist save/restore code.
    return ["javac", "-cp", "/lib/json.jar", str(p)]


def run_java(p: Path) -> List[str]:
    # Frame emits capitalized class file (Canary.java → Canary.class).
    # Our harness wraps it with an additional CanaryMain class in the
    # same file, so javac produces both classes.
    cls = p.stem
    return ["java", "-cp", f"/lib/json.jar:{p.parent}", f"{cls}Main"]


def compile_kotlin(p: Path) -> List[str]:
    # kotlinc writes a jar. org.json is shipped at /lib/json.jar in
    # docker-kotlin; the persist save_state/restore_state code imports
    # it, so it's needed at compile AND run time. -J-Xmx2g mirrors the
    # Kotlin docker runner which OOMs with the default heap.
    jar = p.with_suffix(".jar")
    return [
        "kotlinc", "-J-Xmx2g", "-cp", "/lib/json.jar",
        str(p), "-include-runtime", "-d", str(jar),
    ]


def run_kotlin(p: Path) -> List[str]:
    # Kotlin generates the file-level main class by capitalizing the
    # source filename and appending `Kt`, e.g. `case.kt` → `CaseKt`.
    jar = p.with_suffix(".jar")
    main_class = p.stem[:1].upper() + p.stem[1:] + "Kt"
    return [
        "java", "-cp", f"/lib/json.jar:{jar}",
        main_class,
    ]


def compile_swift(p: Path) -> List[str]:
    bin_path = p.with_suffix("")
    return ["swiftc", str(p), "-o", str(bin_path)]


def run_swift(p: Path) -> List[str]:
    # Prefix `./` for bare filenames (docker pool cwd mode); leave
    # absolute paths (host mode) alone.
    bin_path = p.with_suffix("")
    if bin_path.is_absolute():
        return [str(bin_path)]
    return [f"./{bin_path}"]


def compile_cpp(p: Path) -> List[str]:
    bin_path = p.with_suffix("")
    return ["g++", "-std=c++23", str(p), "-o", str(bin_path)]


def run_cpp(p: Path) -> List[str]:
    bin_path = p.with_suffix("")
    if bin_path.is_absolute():
        return [str(bin_path)]
    return [f"./{bin_path}"]


def compile_csharp(p: Path) -> List[str]:
    # dotnet needs a .csproj; create a minimal one in-place.
    proj_dir = p.parent / "cs_proj"
    proj_dir.mkdir(exist_ok=True)
    csproj = proj_dir / "harness.csproj"
    if not csproj.exists():
        csproj.write_text("""<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <RootNamespace>Harness</RootNamespace>
    <StartupObject>CanaryMain</StartupObject>
  </PropertyGroup>
</Project>
""")
    # Copy the source into the proj dir.
    import shutil as _sh
    _sh.copy(p, proj_dir / "case.cs")
    return ["dotnet", "build", "--nologo", "-v", "quiet", str(proj_dir)]


def run_csharp(p: Path) -> List[str]:
    proj_dir = p.parent / "cs_proj"
    return ["dotnet", "run", "--project", str(proj_dir), "--no-build"]


_RUST_CARGO_TOML = (
    "[package]\n"
    "name = \"diff_harness_case\"\n"
    "version = \"0.0.0\"\n"
    "edition = \"2021\"\n"
    "\n"
    "[[bin]]\n"
    "name = \"case\"\n"
    "path = \"src/main.rs\"\n"
    "\n"
    "[dependencies]\n"
    "serde_json = \"1\"\n"
    # `futures` provides `executor::block_on` — the smallest dep
    # that lets the async fuzz cases drive a `Future` to completion
    # without dragging in a full runtime (tokio, async-std). Cases
    # without `await` ignore the dep; cargo still resolves it.
    "futures = \"0.3\"\n"
    "\n"
    "[profile.dev]\n"
    "debug = false\n"
    "incremental = false\n"
    "opt-level = 0\n"
)


def compile_rust(p: Path) -> List[str]:
    # Per-case Cargo project alongside the emitted `main.rs` so
    # concurrent cases don't clobber each other's source. The
    # emitted path is the case's `<case>.rs`; we stage it as
    # `./src/main.rs` next to a freshly-written `Cargo.toml`, then
    # `cargo build` in that directory.
    import shutil as _sh
    proj = p.parent
    src_dir = proj / "src"
    src_dir.mkdir(exist_ok=True)
    _sh.copy(p, src_dir / "main.rs")
    (proj / "Cargo.toml").write_text(_RUST_CARGO_TOML)
    return [
        "cargo", "build", "--quiet",
        "--manifest-path", str(proj / "Cargo.toml"),
    ]


def run_rust(p: Path) -> List[str]:
    proj = p.parent
    return [str(proj / "target" / "debug" / "case")]


def _which(cmd: str) -> Optional[str]:
    import shutil
    return shutil.which(cmd)


# --- Registry ---
#
# Only Python, JS, TS initially — Phase 1.3 expands this. Every entry
# is a promise: the canary test must produce the exact oracle trace
# with this Lang's wrapper.

import re


def _string_ranges(src: str) -> list[tuple[int, int]]:
    """Return [start, end) byte ranges for every string literal in `src`.

    Scans `"..."`, `'...'`, and `` `...` `` (JS/TS backtick strings),
    handling `\\` escapes. Frame-source corpora don't embed exotic
    string forms (raw strings, triple-quoted heredocs), so this simple
    tracker is sufficient for the harness-level rewrites.

    Comments are not tracked because generated Frame sources the harness
    operates on never contain them."""
    ranges: list[tuple[int, int]] = []
    n = len(src)
    i = 0
    while i < n:
        c = src[i]
        if c in ('"', "'", "`"):
            start = i
            quote = c
            i += 1
            while i < n:
                if src[i] == '\\' and i + 1 < n:
                    i += 2
                    continue
                if src[i] == quote:
                    i += 1
                    break
                i += 1
            ranges.append((start, i))
        else:
            i += 1
    return ranges


def _sub_outside_strings(pattern: str, repl, src: str) -> str:
    """Run `re.sub(pattern, repl, src)` but ignore matches whose start
    position falls inside a string literal. `repl` may be a template
    string (supporting `\\1` / `\\g<name>` backreferences) or a
    callable receiving the match object. Mirrors the string-literal-
    aware rewrite approach used by `replace_outside_strings_and_comments`
    in framec's `codegen_utils`."""
    compiled = re.compile(pattern)
    ranges = _string_ranges(src)

    def inside_string(pos: int) -> bool:
        for start, end in ranges:
            if start <= pos < end:
                return True
        return False

    if callable(repl):
        def sub_fn(m):
            return m.group(0) if inside_string(m.start()) else repl(m)
    else:
        def sub_fn(m):
            return m.group(0) if inside_string(m.start()) else m.expand(repl)

    return compiled.sub(sub_fn, src)


def _rewrite_self(src: str, to: str) -> str:
    """Substitute `self.` → `to` (`this.`, `s.`, `$this->`, …) in the
    Frame body so a Python-flavored pure-Frame source renders correctly
    in the target backend. String-literal-aware so `self.` inside a
    TRACE string literal stays intact. Also preserves Frame's own
    `@@:self.<method>()` construct — that's framec syntax, not a
    native `self.` access."""
    return _sub_outside_strings(
        r'(?<!@@:)\bself\.(?=[A-Za-z_])', to, src,
    )


def _lower_bool(src: str) -> str:
    """Lowercase `True`/`False` → `true`/`false`. Word-boundary anchored
    so identifiers like `False_flag` aren't touched, and string-literal-
    aware so `"True"` / `"False"` in quoted text are preserved."""
    src = _sub_outside_strings(r'\bTrue\b', 'true', src)
    src = _sub_outside_strings(r'\bFalse\b', 'false', src)
    return src


def _map_str_type(src: str, native: str) -> str:
    """Replace Frame's portable `str` type keyword with the target's
    native string type (e.g. `String` in Rust/C#/Java, `string` in Go).
    Matches only when preceded by `:` (optional whitespace) so it's
    clearly a type annotation, and only outside string literals."""
    return _sub_outside_strings(r'(?<=:\s)str\b', native, src)


def _map_bool_type(src: str, native: str) -> str:
    """Replace Frame's portable `bool` type keyword with the target's
    native boolean type (e.g. `boolean` in Java/Kotlin). Positional
    match mirrors `_map_str_type`."""
    return _sub_outside_strings(r'(?<=:\s)bool\b', native, src)


def _transform_py_if_blocks(
    src: str,
    *,
    open_suffix: str,
    else_token: str,
    close_token: str,
) -> str:
    """Rewrite Python-style indent-based `if X: … else: …` blocks to a
    block-delimited form. Used by per-backend `rewrite_trace` helpers to
    translate the pure-Frame generator's canonical Python-style control
    flow into each target's native syntax.

    Parameters (per-target syntax tokens):
      open_suffix  — appended after `if <COND>` on the opener line.
                     C-family: ` {`;  Lua: ` then`;  Ruby: `` (bare).
      else_token   — replaces `else:` when dedented to the if's indent.
                     C-family: `} else {`; Ruby/Lua: `else`.
      close_token  — emitted at the if's indent when the body dedents.
                     C-family: `}`; Ruby/Lua: `end`; Python: `` (none).

    Also wraps the condition in `(...)` for C-family (open_suffix
    starts with ` {`) since those langs require parens around the
    predicate. Other targets keep the condition bare.

    Scope: handles simple single-level `if COND: / else:` blocks with
    consistent indentation — the only shape the Phase-3 generator
    emits. Does NOT handle `elif`, nested ifs, or multi-line
    conditions (none of which the generator produces).
    """
    needs_parens = open_suffix.lstrip().startswith("{")
    lines = src.split('\n')
    out: list[str] = []
    # Stack of indent-columns of currently-open if blocks.
    open_ifs: list[int] = []
    if_re = re.compile(r'^(\s*)if\s+(.+):\s*$')

    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # Close any open ifs we've dedented out of (unless the current
        # line is the matching `else:`, in which case keep the block
        # open so `else_token` gets a chance to fire).
        while (
            open_ifs
            and indent <= open_ifs[-1]
            and not (indent == open_ifs[-1] and stripped == 'else:')
        ):
            close_at = open_ifs.pop()
            if close_token:
                out.append(' ' * close_at + close_token)

        # Opening: `if COND:` → `if COND<open_suffix>` (parens for
        # C-family).
        m = if_re.match(line)
        if m:
            open_indent = len(m.group(1))
            cond = m.group(2).strip()
            head = f'if ({cond})' if needs_parens else f'if {cond}'
            out.append(f'{" " * open_indent}{head}{open_suffix}')
            open_ifs.append(open_indent)
            continue

        # Matching `else:` at the open if's indent.
        if open_ifs and indent == open_ifs[-1] and stripped == 'else:':
            out.append(f'{" " * indent}{else_token}')
            continue

        out.append(line)

    while open_ifs:
        close_at = open_ifs.pop()
        if close_token:
            out.append(' ' * close_at + close_token)
    return '\n'.join(out)


def _py_if_to_c_family(src: str) -> str:
    return _transform_py_if_blocks(
        src, open_suffix=' {', else_token='} else {', close_token='}',
    )


def _py_if_to_ruby(src: str) -> str:
    return _transform_py_if_blocks(
        src, open_suffix='', else_token='else', close_token='end',
    )


def _py_if_to_lua(src: str) -> str:
    return _transform_py_if_blocks(
        src, open_suffix=' then', else_token='else', close_token='end',
    )


def _py_passthrough(src: str) -> str:
    return src


def _js_trace(src: str) -> str:
    # print("x") → console.log("x"); with statement terminator.
    src = _sub_outside_strings(r'\bprint\((.*?)\)', r'console.log(\1);', src)
    src = _rewrite_self(src, "this.")
    src = _py_if_to_c_family(src)
    # Bare `name = await foo(...)` — JS strict mode (.mjs default)
    # rejects assignment to an undeclared identifier. Prepend `let `
    # so the generator can keep emitting Python-canonical bodies.
    # Anchored on a preceding newline (statement boundary) since
    # `_sub_outside_strings` compiles without MULTILINE; only matches
    # when the LHS isn't already qualified (`this.`, `let `, etc.).
    src = _sub_outside_strings(
        r'(\n\s*)([a-zA-Z_]\w*)\s*=\s*await\s+',
        r'\1let \2 = await ',
        src,
    )
    return _lower_bool(src)


def _go_trace(src: str) -> str:
    # print("x") → fmt.Println("x")
    src = _sub_outside_strings(r'\bprint\((.*?)\)', r'fmt.Println(\1)', src)
    # Go's generated methods use `s` as the receiver name. Native
    # statement bodies inside @@state handlers pass through unchanged
    # (Oceans Model), so we must pre-rewrite `self.` → `s.` at the
    # harness layer. The @@:() return-expression path is rewritten
    # inside framec itself (see frame_expansion.rs Go branches).
    src = _rewrite_self(src, "s.")
    src = _py_if_to_c_family(src)
    return _lower_bool(src)


def _ruby_trace(src: str) -> str:
    # print("x") → puts "x" (drop parens); and in Ruby, `print` without
    # parens is also valid but we normalize to `puts` for newline.
    src = _sub_outside_strings(r'\bprint\((.*?)\)', r'puts \1', src)
    # Ruby uses `self.x` natively; no self→this rewrite needed.
    src = _py_if_to_ruby(src)
    return _lower_bool(src)


def _lua_trace(src: str) -> str:
    # print("x") is valid Lua as-is. Passthrough.
    # Lua field access is `self.x` but METHOD dispatch uses colon:
    # `self:op()` passes self as first arg; `self.op()` does not
    # (and explodes if op touches self). The canonical Python-style
    # fuzz source writes `self.Op()`; we rewrite to `self:Op()` for
    # the declared-op names the Phase-5 generator uses. Field access
    # (e.g., `self.counter`) stays dot.
    for op_name in ("Op", "OpOuter", "Bump"):
        src = _sub_outside_strings(
            rf'\bself\.{op_name}\(',
            f'self:{op_name}(',
            src,
        )
    src = _py_if_to_lua(src)
    return _lower_bool(src)


def _rust_trace(src: str) -> str:
    # print("x") → println!("x");  — Rust requires the trailing `;`
    src = _sub_outside_strings(r'\bprint\((.*?)\)', r'println!(\1);', src)
    # Rust uses `self.x` natively; no rewrite needed.
    # Frame `str` maps to `String` in Rust (owned). A bare literal
    # `"hello"` is `&'static str` and does not coerce to `String`
    # without an explicit conversion. In `return <literal>;` sites
    # this is a type error. Wrap string literals with `.to_string()`
    # so the canonical Python-style fuzz source compiles. We only
    # touch the common `return "<lit>";` and `= "<lit>";` forms —
    # anything else stays native.
    src = _sub_outside_strings(
        r'\breturn\s+"([^"]*)";',
        r'return "\1".to_string();',
        src,
    )
    # Python prefix `await EXPR` → Rust postfix `EXPR.await`. Two
    # call shapes from the async fuzz generator:
    #   `await op(key)`        — bare identifier arg (handler param)
    #   `await op("literal")`  — string literal arg (two_phase_init)
    # The first form needs the `&` prefix so the owned `String` key
    # parameter can be re-borrowed across multiple awaits in
    # `two_awaits`. The literal form takes `&str` directly without
    # the prefix.
    src = re.sub(
        r'\bawait\s+([a-zA-Z_]\w*)\(([a-zA-Z_]\w*)\)',
        r'\1(&\2).await',
        src,
    )
    src = re.sub(
        r'\bawait\s+([a-zA-Z_]\w*)\("([^"]*)"\)',
        r'\1("\2").await',
        src,
    )
    src = _py_if_to_c_family(src)
    return _lower_bool(src)


def _php_trace(src: str) -> str:
    # print("x") → echo "x" . PHP_EOL;  — echo + newline, with terminator.
    # Also escape `$` inside the captured string so PHP doesn't try to
    # interpolate `$A` (which it would otherwise read as an undefined
    # variable and stringify to the empty string).
    def _fix(m: re.Match) -> str:
        body = m.group(1)  # the "..." literal including quotes
        escaped = body.replace('$', r'\$')
        return f'echo {escaped} . PHP_EOL;'
    src = _sub_outside_strings(r'\bprint\(("[^"]*")\)', _fix, src)
    # PHP uses `$this->` for self and `$<name>` for variables. Frame
    # bodies in our Phase-2 corpus are Python-flavored (`self.x = v;`);
    # rewrite the two patterns outside string literals:
    #   self.<ident>  →  $this-><ident>
    #   bare `v` rvalue assignments (`= v;`) → `= $v;`
    # PHP types aren't accepted as Frame annotations in the domain
    # block the way Python accepts them, so we strip `: int` / `: str`
    # / `: bool` from interface/param declarations for the PHP backend.
    src = _rewrite_self(src, '$this->')
    src = _sub_outside_strings(r'=\s*v\s*;', '= $v;', src)
    src = _py_if_to_c_family(src)
    return _lower_bool(src)


def _dart_trace(src: str) -> str:
    # `print("x")` is valid Dart. Need terminator and `$` escape — Dart
    # interpolates `$foo` in double-quoted strings.
    def _fix(m: re.Match) -> str:
        lit = m.group(1).replace('$', r'\$')
        return f'print({lit});'
    src = _sub_outside_strings(r'\bprint\(("[^"]*")\)', _fix, src)
    src = _rewrite_self(src, "this.")
    src = _py_if_to_c_family(src)
    return _lower_bool(src)


def _java_trace(src: str) -> str:
    # Java's `map_type` now handles `str` → `String` and `bool` →
    # `boolean` at framec-emit time (see backends/java.rs::emit_field),
    # so the harness no longer needs to rewrite type annotations.
    src = _sub_outside_strings(r'\bprint\(("[^"]*")\)', r'System.out.println(\1);', src)
    src = _rewrite_self(src, 'this.')
    src = _py_if_to_c_family(src)
    # Async fuzz: Python prefix `await op(key)` → Java
    # `op(key).join()` (CompletableFuture's unchecked-exception
    # blocking accessor; `.get()` would force the handler to declare
    # `throws ExecutionException, InterruptedException` and the
    # framec-generated signature can't be tweaked from the harness).
    # Two call shapes, same as Rust:
    #   `await op(<ident>)`    → bare-ident arg (handler param)
    #   `await op("<literal>")` → string-literal arg (two_phase_init)
    src = re.sub(
        r'\bawait\s+([a-zA-Z_]\w*)\(([a-zA-Z_]\w*)\)',
        r'\1(\2).join()',
        src,
    )
    src = re.sub(
        r'\bawait\s+([a-zA-Z_]\w*)\("([^"]*)"\)',
        r'\1("\2").join()',
        src,
    )
    # `op` is a static method on the `Helpers` companion class (same
    # convention as C#'s async fuzz). Bare `op(...)` inside Async<NNNN>
    # handlers doesn't resolve across classes; qualify the call site.
    src = _sub_outside_strings(
        r'(?<!\.)\bop\(',
        r'Helpers.op(',
        src,
    )
    return _lower_bool(src)


def _kotlin_trace(src: str) -> str:
    # println("x") — no trailing `;` required. Escape `$` (Kotlin
    # interpolates in double-quoted strings).
    def _fix(m: re.Match) -> str:
        lit = m.group(1).replace('$', r'\$')
        return f'println({lit})'
    src = _sub_outside_strings(r'\bprint\(("[^"]*")\)', _fix, src)
    src = _rewrite_self(src, "this.")
    src = _map_str_type(src, "String")
    src = _map_bool_type(src, "Boolean")
    src = _py_if_to_c_family(src)
    # Async fuzz: Python `await op(key)` → Kotlin bare `Helpers.op(key)`.
    # Kotlin's `suspend fun` calls don't need explicit `await` when in a
    # coroutine context (the framec dispatch chain runs inside
    # `runBlocking { ... }`). Drop the `await ` keyword and qualify
    # the call.
    src = re.sub(
        r'\bawait\s+([a-zA-Z_]\w*)\(([a-zA-Z_]\w*)\)',
        r'Helpers.\1(\2)',
        src,
    )
    return _lower_bool(src)


def _swift_trace(src: str) -> str:
    # print("x") is valid Swift. Swift only interpolates `\(expr)` —
    # `$foo` is literal — so no escape needed for our canary.
    src = _sub_outside_strings(r'\bprint\(("[^"]*")\)', r'print(\1)', src)
    # Swift uses `self.x` natively; no rewrite needed.
    src = _py_if_to_c_family(src)
    return _lower_bool(src)


def _gdscript_trace(src: str) -> str:
    # GDScript uses `true`/`false` lowercase and `self.x` natively.
    # `print(...)` is valid as-is.
    # Async fuzz: `op` lives on the `Helpers` inner class (cross-
    # class scoping — see `gdscript_async`). Qualify bare `op(`
    # calls inside Async<NNNN> handlers; idempotent via the `(?<!\.)`
    # lookbehind on already-qualified calls.
    src = _sub_outside_strings(
        r'(?<!\.)\bop\(',
        r'Helpers.op(',
        src,
    )
    return _lower_bool(src)


def _erlang_trace(src: str) -> str:
    # Erlang treats Capitalized identifiers as variables; the canonical
    # Python bool atoms `True`/`False` would be read as unbound vars.
    # Atoms are lowercase. No `;`-stripping needed here — framec's
    # Erlang codegen (`erlang_system.rs::rewrite_line`) now trims a
    # trailing `;` from the RHS before constructing the record update.
    #
    # Python-indent `if X:` / `else:` is bridged through brace syntax
    # (`if X { … } else { … }`) so framec's `erlang_transform_blocks`
    # can convert it to Erlang `case (X) of true -> …; false -> … end`.
    # Without this preprocessor the Python syntax passes through
    # verbatim — emitting `if X:` which is a parse error in Erlang.
    # Unlocks Phase-3 selfcall + Phase-4 HSM `if_guarded` and
    # `if_both_arms` axes on Erlang.
    src = _py_if_to_c_family(src)
    return _lower_bool(src)


def _c_trace(src: str) -> str:
    # C uses pointer-to-struct access (`self->x`) rather than dot.
    # `str` in Frame maps to `char*` in the C backend.
    # Method dispatch in C has no dot/arrow form; framec emits ops
    # as free functions `<SysName>_<OpName>(self, …)`. The canonical
    # Python-style fuzz source writes `self.Op()` — we rewrite to
    # `<SysName>_Op(self)` for the declared-op names the Phase-5
    # generator uses. Extract SysName from the first `@@system` line.
    m = re.search(r'@@system\s+([A-Za-z_][A-Za-z0-9_]*)\b', src)
    sys_name = m.group(1) if m else None
    if sys_name is not None:
        for op_name in ("Op", "OpOuter", "Bump"):
            # `self.Op()` (no-arg) → `<Sys>_Op(self)`
            src = _sub_outside_strings(
                rf'\bself\.{op_name}\(\)',
                f'{sys_name}_{op_name}(self)',
                src,
            )
            # `self.Op(a, b)` (with args) → `<Sys>_Op(self, a, b)`
            src = _sub_outside_strings(
                rf'\bself\.{op_name}\(([^)]+)\)',
                rf'{sys_name}_{op_name}(self, \1)',
                src,
            )
    src = _rewrite_self(src, 'self->')
    src = _sub_outside_strings(r'(?<=:\s)str\b', 'char*', src)
    src = _py_if_to_c_family(src)
    return _lower_bool(src)


def _cpp_trace(src: str) -> str:
    src = _sub_outside_strings(
        r'\bprint\(("[^"]*")\)',
        r'std::cout << \1 << std::endl;',
        src,
    )
    src = _rewrite_self(src, 'this->')
    src = _map_str_type(src, "std::string")
    src = _py_if_to_c_family(src)
    return _lower_bool(src)


def _csharp_trace(src: str) -> str:
    # C#'s `map_type` now handles `str` → `string` at framec-emit
    # time (see backends/csharp.rs::emit_field), so the harness no
    # longer needs `_map_str_type`.
    src = re.sub(r'\bprint\(("[^"]*")\)', r'System.Console.WriteLine(\1);', src)
    # Async fuzz: `op` is a static method on the `Helpers` companion
    # class (matches Java's convention). Inside Async<NNNN>.<handler>
    # bodies, bare `op(key)` doesn't resolve across classes —
    # qualify the call site. Idempotent (already-qualified calls
    # have a `.` before `op` and are skipped via the lookbehind).
    src = _sub_outside_strings(
        r'(?<!\.)\bop\(',
        r'Helpers.op(',
        src,
    )
    src = _rewrite_self(src, "this.")
    src = _py_if_to_c_family(src)
    return _lower_bool(src)


LANGS = {
    "python_3": Lang(
        name="python_3",
        ext="fpy",
        out_ext="py",
        run=run_python,
        save_method="save_state",
        restore_call="{S}.restore_state({B})",
        render_canary=py_canary,
        renderers={'persist': py_persist, 'selfcall': py_selfcall, 'hsm': py_hsm, 'operations': py_operations, 'nested': py_nested, 'async': py_async, 'multisys': py_multisys},
        rewrite_trace=_py_passthrough,
        notes="Pickle blob. staticmethod restore_state. Oracle reference.",
    ),
    "javascript": Lang(
        name="javascript",
        ext="fjs",
        out_ext="js",
        run=run_node_esm,
        save_method="saveState",
        restore_call="{S}.restoreState({B})",
        render_canary=js_canary,
        renderers={'persist': js_persist, 'selfcall': js_selfcall, 'hsm': js_hsm, 'operations': js_operations, 'nested': js_nested, 'async': js_async, 'multisys': js_multisys},
        rewrite_trace=_js_trace,
        notes="JSON string blob. camelCase methods. Requires .mjs for ESM.",
    ),
    "typescript": Lang(
        name="typescript",
        ext="fts",
        out_ext="ts",
        run=run_ts,
        save_method="saveState",
        restore_call="{S}.restoreState({B})",
        render_canary=ts_canary,
        renderers={'persist': js_persist, 'selfcall': js_selfcall, 'hsm': js_hsm, 'operations': ts_operations, 'nested': ts_nested, 'async': ts_async, 'multisys': js_multisys},  # JS & TS share persist harness text
        rewrite_trace=_js_trace,  # same syntax as JS
        notes="JSON string blob. Same method names as JavaScript.",
    ),
    "go": Lang(
        name="go",
        ext="fgo",
        out_ext="go",
        run=run_go,
        save_method="SaveState",
        restore_call="Restore{S}({B})",  # package-level function
        render_canary=go_canary,
        # NOTE: 'multisys' renderer (go_multisys) is implemented but
        # unwired — framec's Go backend emits `NewCounter()` returning
        # `*Counter` but types the domain field as `Counter` (by
        # value), so the assignment fails type-check. Real framec gap;
        # tracked as Phase 7 follow-up.
        renderers={'persist': go_persist, 'selfcall': go_selfcall, 'hsm': go_hsm, 'operations': go_operations, 'nested': go_nested},
        rewrite_trace=_go_trace,
        prolog='package main\n\nimport (\n\t"encoding/json"\n\t"fmt"\n)\n\nvar _ = json.Marshal\n',
        notes="JSON blob. PascalCase methods. Restore is pkg-level `RestoreP()`.",
    ),
    "ruby": Lang(
        name="ruby",
        ext="frb",
        out_ext="rb",
        run=run_ruby,
        save_method="save_state",
        restore_call="{S}.restore_state({B})",
        render_canary=ruby_canary,
        renderers={'persist': ruby_persist, 'selfcall': ruby_selfcall, 'hsm': ruby_hsm, 'operations': ruby_operations, 'nested': ruby_nested, 'multisys': ruby_multisys},
        rewrite_trace=_ruby_trace,
        prolog="require 'json'\n",
        notes="JSON blob. snake_case methods, classmethod restore_state.",
    ),
    "lua": Lang(
        name="lua",
        ext="flua",
        out_ext="lua",
        run=run_lua,
        save_method="save_state",
        restore_call="{S}.restore_state({B})",
        render_canary=lua_canary,
        # NOTE: 'multisys' renderer (lua_multisys) is implemented but
        # unwired — framec's Lua codegen for cross-system method
        # calls binds `self` to nil at the inner-method call site
        # (`attempt to index a nil value (local 'self')`). Real
        # framec gap; tracked as Phase 7 follow-up.
        renderers={'persist': lua_persist, 'selfcall': lua_selfcall, 'hsm': lua_hsm, 'operations': lua_operations, 'nested': lua_nested},
        rewrite_trace=_lua_trace,
        docker_image="docker-lua",
        notes=(
            "JSON blob via cjson. Runs via docker-lua since macOS's "
            "system lua lacks cjson; the container ships it preinstalled."
        ),
    ),
    "gdscript": Lang(
        name="gdscript",
        ext="fgd",
        out_ext="gd",
        save_method="save_state",
        restore_call="{S}.restore_state({B})",
        renderers={'persist': gdscript_persist, 'selfcall': gdscript_selfcall, 'hsm': gdscript_hsm, 'operations': gdscript_operations, 'nested': gdscript_nested, 'async': gdscript_async, 'multisys': gdscript_multisys},
        run_custom=gdscript_run_custom,
        rewrite_trace=_gdscript_trace,
        docker_image="docker-gdscript",  # informational; custom hook wraps itself
        # GDScript `extends SceneTree` gives us access to `quit()` and
        # lets us use `func _init()` as the entry point.
        prolog="extends SceneTree\n",
        notes=(
            "Runs via `godot --headless --script` in docker-gdscript. "
            "Engine banner is stripped from stdout by the custom hook."
        ),
    ),
    "c": Lang(
        name="c",
        ext="fc",
        out_ext="c",
        compile=compile_c,
        run=run_c,
        save_method="save_state",
        restore_call="{S}_restore_state({B})",
        renderers={'persist': c_persist, 'selfcall': c_selfcall, 'hsm': c_hsm, 'operations': c_operations, 'nested': c_nested},
        rewrite_trace=_c_trace,
        docker_image="docker-c",
        # framec's C codegen uses cJSON and bool; user-supplied includes
        # are stdio (for printf trace) + cJSON (for serialization) +
        # stdbool (for `true`/`false` literals). Compiled with `-lcjson`
        # in the docker-c container.
        prolog="#include <stdio.h>\n#include <stdlib.h>\n#include <stdbool.h>\n#include <cjson/cJSON.h>\n",
        notes=(
            "Pointer-based ABI: `SysName_method(self, args)`. The custom "
            "rewriter translates `self.` to `self->` and `str` to "
            "`char*` since framec's C backend doesn't auto-translate "
            "those from the portable Frame keywords. Compiled inside "
            "docker-c with `gcc -lcjson`."
        ),
    ),
    "erlang": Lang(
        name="erlang",
        ext="ferl",
        out_ext="erl",
        save_method="save_state",
        restore_call="{S}:load_state({B})",  # note: load_state, not restore
        # Erlang uses a custom runner instead of the standard compile+run
        # path: framec emits a .erl that needs to be renamed to match the
        # `-module(...)` directive, then compiled via `erlc`, then driven
        # by an escript (not a main() call). The custom hook handles all
        # four steps and returns an Erlang trace matching the oracle.
        run_custom=erlang_run_custom,
        case_supported=erlang_case_supported,
        rewrite_trace=_erlang_trace,
        docker_image="docker-erlang",  # informational; custom hook wraps itself
        notes=(
            "gen_statem process model. PascalCase Frame names map to "
            "snake_case Erlang module names (Persist0000 → persist0000). "
            "Persist API uses load_state/1 not restore_state/1."
        ),
    ),
    "rust": Lang(
        name="rust",
        ext="frs",
        out_ext="rs",
        compile=compile_rust,
        run=run_rust,
        save_method="save_state",
        restore_call="{S}::restore_state({B})",
        render_canary=rust_canary,
        renderers={'persist': rust_persist, 'selfcall': rust_selfcall, 'hsm': rust_hsm, 'operations': rust_operations, 'nested': rust_nested, 'async': rust_async, 'multisys': rust_multisys},
        case_supported=rust_async_supported,
        rewrite_trace=_rust_trace,
        notes="JSON string. save_state(&mut self), restore_state(json: String).",
    ),
    "php": Lang(
        name="php",
        ext="fphp",
        out_ext="php",
        run=run_php,
        save_method="save_state",
        restore_call="{S}::restore_state({B})",
        render_canary=php_canary,
        # NOTE: 'multisys' renderer (php_multisys) is implemented but
        # unwired — framec emits `new {{name}}()` in a context PHP's
        # parser rejects ("New expressions are not supported in this
        # context"). Real framec gap; tracked as Phase 7 follow-up.
        renderers={'persist': php_persist, 'selfcall': php_selfcall, 'hsm': php_hsm, 'operations': php_operations, 'nested': php_nested},
        rewrite_trace=_php_trace,
        prolog="<?php\n",
        notes="JSON string blob. static restore_state. New() fires constructor.",
    ),
    "dart": Lang(
        name="dart",
        ext="fdart",
        out_ext="dart",
        run=run_dart,
        save_method="saveState",
        restore_call="{S}.restoreState({B})",
        render_canary=dart_canary,
        renderers={'persist': dart_persist, 'selfcall': dart_selfcall, 'hsm': dart_hsm, 'operations': dart_operations, 'nested': dart_nested, 'async': dart_async, 'multisys': dart_multisys},
        rewrite_trace=_dart_trace,
        prolog="import 'dart:convert';\n",
        notes="JSON string. camelCase methods (saveState/restoreState).",
    ),
    "java": Lang(
        name="java",
        ext="fjava",
        out_ext="java",
        compile=compile_java,
        run=run_java,
        save_method="save_state",
        restore_call="{S}.restore_state({B})",
        render_canary=java_canary,
        # NOTE: 'multisys' renderer is implemented but unwired —
        # framec emits E407 ("Java allows only one public class per
        # file") for multi-system files. Per FUZZ_PLAN.md Phase 7
        # Java is excluded alongside Erlang for the same reason.
        renderers={'persist': java_persist, 'selfcall': java_selfcall, 'hsm': java_hsm, 'operations': java_operations, 'nested': java_nested, 'async': java_async},
        rewrite_trace=_java_trace,
        docker_image="docker-java",
        notes=(
            "JSON string. snake_case methods. Uses docker-java image which "
            "ships org.json at /lib/json.jar — harness wraps compile + run "
            "via _docker_wrap so the classpath resolves inside the container."
        ),
    ),
    "kotlin": Lang(
        name="kotlin",
        ext="fkt",
        out_ext="kt",
        compile=compile_kotlin,
        run=run_kotlin,
        save_method="save_state",
        restore_call="{S}.restore_state({B})",
        render_canary=kotlin_canary,
        # NOTE: 'async' renderer (kotlin_async) is implemented but not
        # wired in — the harness's docker-kotlin image only ships
        # `/lib/json.jar` on the kotlinc classpath; kotlinx.coroutines
        # isn't available so `runBlocking` doesn't resolve. Adding the
        # coroutines jar to the docker image (or vendoring it under
        # /lib/) would unblock Kotlin async fuzz; tracked as Phase 6
        # follow-up in `memory/phase6_async_2026_04_27.md`.
        renderers={'persist': kotlin_persist, 'selfcall': kotlin_selfcall, 'hsm': kotlin_hsm, 'operations': kotlin_operations, 'nested': kotlin_nested},
        rewrite_trace=_kotlin_trace,
        docker_image="docker-kotlin",
        # kotlinc -J-Xmx2g: 2GB heap per invocation. At --jobs=14 that's
        # 28GB; a 16GB host OOMs. Cap at 2 concurrent kotlincs.
        concurrency_limit=2,
        notes=(
            "JSON string. Builds a fat jar via kotlinc. Also needs org.json; "
            "same docker-only constraint as java."
        ),
    ),
    "swift": Lang(
        name="swift",
        ext="fswift",
        out_ext="swift",
        compile=compile_swift,
        run=run_swift,
        save_method="saveState",
        restore_call="{S}.restoreState({B})",
        render_canary=swift_canary,
        # NOTE: 'async' renderer (swift_async) is implemented but not
        # wired in — local Swift toolchain on macOS dev hosts is
        # 5.3.2 (pre-async/await; Swift 5.5+ required). Docker
        # docker-swift has a recent Swift; wiring requires routing
        # the async fuzz through that image. Tracked as Phase 6
        # follow-up in `memory/phase6_async_2026_04_27.md`.
        renderers={'persist': swift_persist, 'selfcall': swift_selfcall, 'hsm': swift_hsm, 'operations': swift_operations, 'nested': swift_nested},
        rewrite_trace=_swift_trace,
        notes="JSON string. camelCase methods. swiftc produces single binary.",
    ),
    "cpp": Lang(
        name="cpp_23",
        ext="fcpp",
        out_ext="cpp",
        compile=compile_cpp,
        run=run_cpp,
        save_method="save_state",
        restore_call="{S}::restore_state({B})",
        render_canary=cpp_canary,
        renderers={'persist': cpp_persist, 'selfcall': cpp_selfcall, 'hsm': cpp_hsm, 'operations': cpp_operations, 'nested': cpp_nested},
        rewrite_trace=_cpp_trace,
        docker_image="docker-cpp",
        # Framec's C++ codegen references `nlohmann::json` in
        # save_state/restore_state but doesn't emit the include; the
        # user is expected to supply it in the prolog (matches what
        # the existing matrix tests do). `<iostream>` is for the
        # persist harness's `std::cout` calls.
        prolog="#include <iostream>\n#include <nlohmann/json.hpp>\n",
        notes=(
            "JSON string (std::string). Requires C++23. Uses docker-cpp "
            "image (g++ 14+) since macOS Apple clang is typically older."
        ),
    ),
    "csharp": Lang(
        name="csharp",
        ext="fcs",
        out_ext="cs",
        compile=compile_csharp,
        run=run_csharp,
        save_method="SaveState",
        restore_call="{S}.RestoreState({B})",
        render_canary=csharp_canary,
        renderers={'persist': csharp_persist, 'selfcall': csharp_selfcall, 'hsm': csharp_hsm, 'operations': csharp_operations, 'nested': csharp_nested, 'async': csharp_async, 'multisys': csharp_multisys},
        rewrite_trace=_csharp_trace,
        notes="JSON string. PascalCase methods. dotnet csproj + build+run.",
    ),
}

# Deliberately empty for now — Phase 1.3 fills these in with real
# compile/run lambdas per backend once the canary has proven itself
# across python/js/ts.
PENDING_LANGS = [
    "rust", "c", "cpp", "csharp", "java",
    "kotlin", "swift", "go", "php", "ruby",
    "lua", "dart", "gdscript", "erlang",
]
