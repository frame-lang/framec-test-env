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


def _which(cmd: str) -> Optional[str]:
    import shutil
    return shutil.which(cmd)


# --- Registry ---
#
# Only Python, JS, TS initially — Phase 1.3 expands this. Every entry
# is a promise: the canary test must produce the exact oracle trace
# with this Lang's wrapper.

import re


def _py_passthrough(src: str) -> str:
    return src


def _js_trace(src: str) -> str:
    # print("x") → console.log("x"); with statement terminator.
    return re.sub(r'\bprint\((.*?)\)', r'console.log(\1);', src)


def _go_trace(src: str) -> str:
    # print("x") → fmt.Println("x")
    return re.sub(r'\bprint\((.*?)\)', r'fmt.Println(\1)', src)


def _ruby_trace(src: str) -> str:
    # print("x") → puts "x" (drop parens); and in Ruby, `print` without
    # parens is also valid but we normalize to `puts` for newline.
    return re.sub(r'\bprint\((.*?)\)', r'puts \1', src)


def _lua_trace(src: str) -> str:
    # print("x") is valid Lua as-is. Passthrough.
    return src


LANGS = {
    "python_3": Lang(
        name="python_3",
        ext="fpy",
        out_ext="py",
        run=run_python,
        save_method="save_state",
        restore_call="{S}.restore_state({B})",
        render_canary=py_canary,
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
        rewrite_trace=_lua_trace,
        notes="JSON blob. `P:save_state()` method; `P.restore_state(json)` static.",
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
