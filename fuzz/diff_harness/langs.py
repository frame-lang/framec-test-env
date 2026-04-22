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
    <TargetFramework>net9.0</TargetFramework>
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


def _rust_trace(src: str) -> str:
    # print("x") → println!("x");  — Rust requires the trailing `;`
    return re.sub(r'\bprint\((.*?)\)', r'println!(\1);', src)


def _php_trace(src: str) -> str:
    # print("x") → echo "x" . PHP_EOL;  — echo + newline, with terminator.
    # Also escape `$` inside the captured string so PHP doesn't try to
    # interpolate `$A` (which it would otherwise read as an undefined
    # variable and stringify to the empty string).
    def _fix(m: re.Match) -> str:
        body = m.group(1)  # the "..." literal including quotes
        escaped = body.replace('$', r'\$')
        return f'echo {escaped} . PHP_EOL;'
    return re.sub(r'\bprint\(("[^"]*")\)', _fix, src)


def _dart_trace(src: str) -> str:
    # `print("x")` is valid Dart. Need terminator and `$` escape — Dart
    # interpolates `$foo` in double-quoted strings.
    def _fix(m: re.Match) -> str:
        lit = m.group(1).replace('$', r'\$')
        return f'print({lit});'
    return re.sub(r'\bprint\(("[^"]*")\)', _fix, src)


def _java_trace(src: str) -> str:
    return re.sub(r'\bprint\(("[^"]*")\)', r'System.out.println(\1);', src)


def _kotlin_trace(src: str) -> str:
    # println("x") — no trailing `;` required. Escape `$` (Kotlin
    # interpolates in double-quoted strings).
    def _fix(m: re.Match) -> str:
        lit = m.group(1).replace('$', r'\$')
        return f'println({lit})'
    return re.sub(r'\bprint\(("[^"]*")\)', _fix, src)


def _swift_trace(src: str) -> str:
    # print("x") is valid Swift. Swift only interpolates `\(expr)` —
    # `$foo` is literal — so no escape needed for our canary.
    return re.sub(r'\bprint\(("[^"]*")\)', r'print(\1)', src)


def _cpp_trace(src: str) -> str:
    return re.sub(
        r'\bprint\(("[^"]*")\)',
        r'std::cout << \1 << std::endl;',
        src,
    )


def _csharp_trace(src: str) -> str:
    return re.sub(r'\bprint\(("[^"]*")\)', r'System.Console.WriteLine(\1);', src)


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
    "rust": Lang(
        name="rust",
        ext="frs",
        out_ext="rs",
        compile=compile_rust,
        run=run_rust,
        save_method="save_state",
        restore_call="{S}::restore_state({B})",
        render_canary=rust_canary,
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
