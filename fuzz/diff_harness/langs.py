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
from typing import Callable, List, Optional


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
    # Per-language harness rendered AFTER the @@system block. Takes
    # a ignored string placeholder so each harness can grow richer
    # per-case context later.
    render_canary: Optional[Callable[[str], str]] = None
    # Phase-2 persist fuzz harness. Takes the case's meta dict
    # (sys_name + axes + sequence) and returns the native epilog.
    # Every renderer MUST produce the same normalized trace:
    #   TRACE: advance           (advances_pre times)
    #   TRACE: set_x <int>
    #   TRACE: set_s "<str>"     (iff domain has str)
    #   TRACE: set_b true|false  (iff domain has bool)
    #   TRACE: status <sN>
    #   TRACE: save ok
    #   TRACE: restore ok
    #   TRACE: post_status <sN>
    #   TRACE: post_x <int>
    #   TRACE: post_s "<str>"    (iff domain has str)
    #   TRACE: post_b true|false (iff domain has bool)
    #   TRACE: done
    render_persist: Optional[Callable[[dict], str]] = None
    # Rewriter: turn a Python-syntax trace line like
    # `print("TRACE: ...")` into the backend's equivalent. Applied to
    # the @@system block by run_diff. Default assumes `print(...)` is
    # valid in the target (true for Python, Lua, Swift, GDScript, Dart).
    rewrite_trace: Callable[[str], str] = lambda s: s
    # Native prolog injected BEFORE the @@system block, AFTER the
    # @@target directive. Use for `package main` (Go), `require 'json'`
    # (Ruby), etc. Kept separate from the harness because framec
    # requires these as pre-system native code.
    prolog: str = ""
    # Language support notes (free text, informational only).
    notes: str = ""


# --- Persist fuzz harness rendering helpers ---
#
# Each `render_persist` callback receives the case's meta dict from
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
    lines.append(f"    val rest = {sys_name}.restore_state(blob)")
    lines.append('    println("TRACE: restore ok")')
    lines.append('    println("TRACE: post_status ${rest.status()}")')
    lines.append('    println("TRACE: post_x ${rest.get_x()}")')
    if has_str:
        lines.append('    println("TRACE: post_s \\"${rest.get_s()}\\"")')
    if has_bool:
        lines.append(
            '    println("TRACE: post_b ${if (rest.get_b() as Boolean) \\"true\\" else \\"false\\"}")'
        )
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
    lines.append('print("TRACE: post_x " .. tostring(rest:get_x()))')
    if has_str:
        lines.append('print(\'TRACE: post_s "\' .. rest:get_s() .. \'"\')')
    if has_bool:
        # Lua: no ternary; use and/or idiom.
        lines.append(
            "print(\"TRACE: post_b \" .. (rest:get_b() and \"true\" or \"false\"))"
        )
    lines.append('print("TRACE: done")')
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
    # Prefer lua5.4; fall back to plain `lua`.
    return ["lua5.4", str(p)] if _which("lua5.4") else ["lua", str(p)]


def run_php(p: Path) -> List[str]:
    return ["php", str(p)]


def run_dart(p: Path) -> List[str]:
    return ["dart", "run", str(p)]


def compile_java(p: Path) -> List[str]:
    # Frame emits the class under an exact filename; javac produces .class.
    return ["javac", str(p)]


def run_java(p: Path) -> List[str]:
    # Frame emits capitalized class file (Canary.java → Canary.class).
    # Our harness wraps it with an additional CanaryMain class in the
    # same file, so javac produces both classes.
    cls = p.stem
    return ["java", "-cp", str(p.parent), f"{cls}Main"]


def compile_kotlin(p: Path) -> List[str]:
    # kotlinc writes a jar.
    jar = p.with_suffix(".jar")
    return ["kotlinc", str(p), "-include-runtime", "-d", str(jar)]


def run_kotlin(p: Path) -> List[str]:
    return ["java", "-jar", str(p.with_suffix(".jar"))]


def compile_swift(p: Path) -> List[str]:
    bin_path = p.with_suffix("")
    return ["swiftc", str(p), "-o", str(bin_path)]


def run_swift(p: Path) -> List[str]:
    return [str(p.with_suffix(""))]


def compile_cpp(p: Path) -> List[str]:
    bin_path = p.with_suffix("")
    return ["g++", "-std=c++23", str(p), "-o", str(bin_path)]


def run_cpp(p: Path) -> List[str]:
    return [str(p.with_suffix(""))]


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


def compile_rust(p: Path) -> List[str]:
    # Copy emitted source into the pre-built cargo project's
    # src/main.rs and cargo build. Runner then runs the binary.
    import shutil as _sh
    proj = Path(__file__).parent / "rust_proj"
    _sh.copy(p, proj / "src" / "main.rs")
    return ["cargo", "build", "--quiet", "--manifest-path", str(proj / "Cargo.toml")]


def run_rust(p: Path) -> List[str]:
    proj = Path(__file__).parent / "rust_proj"
    return [str(proj / "target" / "debug" / "diff_harness_case")]


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
    TRACE string literal stays intact."""
    return _sub_outside_strings(r'\bself\.(?=[A-Za-z_])', to, src)


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


def _py_passthrough(src: str) -> str:
    return src


def _js_trace(src: str) -> str:
    # print("x") → console.log("x"); with statement terminator.
    src = _sub_outside_strings(r'\bprint\((.*?)\)', r'console.log(\1);', src)
    src = _rewrite_self(src, "this.")
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
    return _lower_bool(src)


def _ruby_trace(src: str) -> str:
    # print("x") → puts "x" (drop parens); and in Ruby, `print` without
    # parens is also valid but we normalize to `puts` for newline.
    src = _sub_outside_strings(r'\bprint\((.*?)\)', r'puts \1', src)
    # Ruby uses `self.x` natively; no self→this rewrite needed.
    return _lower_bool(src)


def _lua_trace(src: str) -> str:
    # print("x") is valid Lua as-is. Passthrough.
    # Lua uses `self.x` natively (in method-colon-call style).
    return _lower_bool(src)


def _rust_trace(src: str) -> str:
    # print("x") → println!("x");  — Rust requires the trailing `;`
    src = _sub_outside_strings(r'\bprint\((.*?)\)', r'println!(\1);', src)
    # Rust uses `self.x` natively; no rewrite needed.
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
    return _sub_outside_strings(r'\bprint\(("[^"]*")\)', _fix, src)


def _dart_trace(src: str) -> str:
    # `print("x")` is valid Dart. Need terminator and `$` escape — Dart
    # interpolates `$foo` in double-quoted strings.
    def _fix(m: re.Match) -> str:
        lit = m.group(1).replace('$', r'\$')
        return f'print({lit});'
    src = _sub_outside_strings(r'\bprint\(("[^"]*")\)', _fix, src)
    src = _rewrite_self(src, "this.")
    return _lower_bool(src)


def _java_trace(src: str) -> str:
    return _sub_outside_strings(r'\bprint\(("[^"]*")\)', r'System.out.println(\1);', src)


def _kotlin_trace(src: str) -> str:
    # println("x") — no trailing `;` required. Escape `$` (Kotlin
    # interpolates in double-quoted strings).
    def _fix(m: re.Match) -> str:
        lit = m.group(1).replace('$', r'\$')
        return f'println({lit})'
    src = _sub_outside_strings(r'\bprint\(("[^"]*")\)', _fix, src)
    src = _rewrite_self(src, "this.")
    return _lower_bool(src)


def _swift_trace(src: str) -> str:
    # print("x") is valid Swift. Swift only interpolates `\(expr)` —
    # `$foo` is literal — so no escape needed for our canary.
    src = _sub_outside_strings(r'\bprint\(("[^"]*")\)', r'print(\1)', src)
    # Swift uses `self.x` natively; no rewrite needed.
    return _lower_bool(src)


def _cpp_trace(src: str) -> str:
    return re.sub(
        r'\bprint\(("[^"]*")\)',
        r'std::cout << \1 << std::endl;',
        src,
    )


def _csharp_trace(src: str) -> str:
    src = re.sub(r'\bprint\(("[^"]*")\)', r'System.Console.WriteLine(\1);', src)
    src = _rewrite_self(src, "this.")
    src = _map_str_type(src, "string")
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
        render_persist=py_persist,
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
        render_persist=js_persist,
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
        render_persist=js_persist,  # JS & TS share persist harness text
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
        render_persist=go_persist,
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
        render_persist=ruby_persist,
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
        render_persist=lua_persist,
        rewrite_trace=_lua_trace,
        notes="JSON blob. `P:save_state()` method; `P.restore_state(json)` static.",
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
        render_persist=rust_persist,
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
        render_persist=dart_persist,
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
        rewrite_trace=_java_trace,
        notes=(
            "JSON string. snake_case methods. Needs org.json on classpath. "
            "DOCKER-ONLY locally — Maven download is blocked by harness policy; "
            "fuzz runs inside the Java container which already ships org.json."
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
        render_persist=kotlin_persist,
        rewrite_trace=_kotlin_trace,
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
        render_persist=swift_persist,
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
        rewrite_trace=_cpp_trace,
        notes=(
            "JSON string (std::string). Requires C++23. DOCKER-ONLY locally if "
            "the host's clang/gcc is older than ~2024 (macOS Apple clang 12 is)."
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
        render_persist=csharp_persist,
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
