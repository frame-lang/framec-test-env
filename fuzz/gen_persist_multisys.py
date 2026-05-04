#!/usr/bin/env python3
"""
Phase 25 — RFC-0015 fuzz: parameterized sub-system × persist round-trip.

Locks in the Issue #2 fix shipped by RFC-0015. The original defect
class: an outer system holds a sub-system in its domain
(`inner: Inner = @@Inner()`), the user calls save_state() on the
outer, restore tries to reconstruct `inner` and crashes.

RFC-0015's factory-only contract eliminates the user-arg constructor:
restore allocates with the empty blank-allocator, then populates from
the saved nested blob. This phase exercises the contract end-to-end.

Pattern P1 — simple_nested:
  outer holds zero-arg Inner. Mutate inner via outer.tick(),
  save outer, restore, verify inner state survived.

The generator is template-driven: each backend supplies its
target-language idioms (type names, receiver syntax, print/exit
calls, main shape) and the same Frame skeleton is rendered per
backend. Adding a new backend is a config dict, not a new function.

Usage:
  python3 gen_persist_multisys.py --max 10
  ./run_persist_multisys.sh
"""
import argparse
from pathlib import Path


# Per-backend template config.
#
# Fields:
#   target          — `@@[target("...")]` string
#   ext             — file extension (without the dot)
#   blob_type       — Frame attribute string for `@@[persist(<T>)]`
#   int_type        — Frame integer-type spelling
#   self_           — handler-body receiver (Frame self prefix)
#   prologue        — text inserted between `@@[target(...)]` and the
#                     first `@@system` (imports etc.)
#   epilogue        — main-function template; uses {tag} placeholder
#                     for the PASS marker.
#
# `epilogue` is the only place backends differ in structural shape;
# Frame source itself is identical.

LANGS = {
    "python_3": {
        "target": "python_3",
        "ext": "fpy",
        "blob_type": "str",
        "int_type": "int",
        "self_": "self",
        "prologue": "",
        "epilogue": '''
if __name__ == "__main__":
    root = Outer()
    root.tick()
    root.tick()
    root.tick()
    if root.get_inner_n() != 3:
        print("FAIL pre: " + str(root.get_inner_n()))
        raise SystemExit(1)

    snap = root.save_state()
    rest = Outer()
    rest.restore_state(snap)
    if rest.get_inner_n() != 3:
        print("FAIL post: " + str(rest.get_inner_n()))
        raise SystemExit(1)

    print("PASS: {tag}")
''',
    },
    "javascript": {
        "target": "javascript",
        "ext": "fjs",
        "blob_type": "string",
        "int_type": "int",
        "self_": "this",
        "prologue": "",
        "epilogue": '''
const root = new Outer();
root.tick();
root.tick();
root.tick();
if (root.getInnerN() !== 3) {{
    console.log("FAIL pre: " + root.getInnerN());
    process.exit(1);
}}
const snap = root.saveState();
const rest = new Outer();
rest.restoreState(snap);
if (rest.getInnerN() !== 3) {{
    console.log("FAIL post: " + rest.getInnerN());
    process.exit(1);
}}
console.log("PASS: {tag}");
''',
    },
    "typescript": {
        "target": "typescript",
        "ext": "fts",
        "blob_type": "string",
        "int_type": "number",
        "self_": "this",
        "prologue": "",
        "epilogue": '''
const root = new Outer();
root.tick();
root.tick();
root.tick();
if (root.getInnerN() !== 3) {{
    console.log("FAIL pre: " + root.getInnerN());
    process.exit(1);
}}
const snap = root.saveState();
const rest = new Outer();
rest.restoreState(snap);
if (rest.getInnerN() !== 3) {{
    console.log("FAIL post: " + rest.getInnerN());
    process.exit(1);
}}
console.log("PASS: {tag}");
''',
    },
    "rust": {
        "target": "rust",
        "ext": "frs",
        "blob_type": "String",
        "int_type": "i32",
        "self_": "self",
        "prologue": "use serde_json;\n\n",
        "epilogue": '''
fn main() {{
    let mut root = Outer::new();
    root.tick();
    root.tick();
    root.tick();
    if root.get_inner_n() != 3 {{
        println!("FAIL pre: {{}}", root.get_inner_n());
        std::process::exit(1);
    }}

    let snap = root.save_state();
    let mut rest = Outer::new();
    rest.restore_state(snap);
    if rest.get_inner_n() != 3 {{
        println!("FAIL post: {{}}", rest.get_inner_n());
        std::process::exit(1);
    }}

    println!("PASS: {tag}");
}}
''',
    },
    "ruby": {
        "target": "ruby",
        "ext": "frb",
        "blob_type": "String",
        "int_type": "int",
        "self_": "self",
        "prologue": "",
        "epilogue": '''
root = Outer.new
root.tick
root.tick
root.tick
if root.get_inner_n != 3
    puts "FAIL pre: #{{root.get_inner_n}}"
    exit 1
end
snap = root.save_state
rest = Outer.new
rest.restore_state(snap)
if rest.get_inner_n != 3
    puts "FAIL post: #{{rest.get_inner_n}}"
    exit 1
end
puts "PASS: {tag}"
''',
    },
    "lua": {
        "target": "lua",
        "ext": "flua",
        "blob_type": "string",
        "int_type": "int",
        "self_": "self",
        "prologue": "",
        "epilogue": '''
local root = Outer:new()
root:tick()
root:tick()
root:tick()
if root:get_inner_n() ~= 3 then
    print("FAIL pre: " .. root:get_inner_n())
    os.exit(1)
end
local snap = root:save_state()
local rest = Outer:new()
rest:restore_state(snap)
if rest:get_inner_n() ~= 3 then
    print("FAIL post: " .. rest:get_inner_n())
    os.exit(1)
end
print("PASS: {tag}")
''',
    },
    "php": {
        "target": "php",
        "ext": "fphp",
        "blob_type": "string",
        "int_type": "int",
        "self_": "$this",
        "prologue": "",
        "epilogue": '''
$root = new Outer();
$root->tick();
$root->tick();
$root->tick();
if ($root->get_inner_n() !== 3) {{
    echo "FAIL pre: " . $root->get_inner_n() . "\\n";
    exit(1);
}}
$snap = $root->save_state();
$rest = new Outer();
$rest->restore_state($snap);
if ($rest->get_inner_n() !== 3) {{
    echo "FAIL post: " . $rest->get_inner_n() . "\\n";
    exit(1);
}}
echo "PASS: {tag}\\n";
''',
    },
    "dart": {
        "target": "dart",
        "ext": "fdart",
        "blob_type": "String",
        "int_type": "int",
        "self_": "this",
        "prologue": "",
        "epilogue": '''
void main() {{
    final root = Outer();
    root.tick();
    root.tick();
    root.tick();
    if (root.get_inner_n() != 3) {{
        print("FAIL pre: ${{root.get_inner_n()}}");
        return;
    }}
    final snap = root.save_state();
    final rest = Outer();
    rest.restore_state(snap);
    if (rest.get_inner_n() != 3) {{
        print("FAIL post: ${{rest.get_inner_n()}}");
        return;
    }}
    print("PASS: {tag}");
}}
''',
    },
    "kotlin": {
        "target": "kotlin",
        "ext": "fkt",
        "blob_type": "String",
        "int_type": "Int",
        "self_": "this",
        "prologue": "",
        "epilogue": '''
fun main() {{
    val root = Outer()
    root.tick()
    root.tick()
    root.tick()
    if (root.get_inner_n() != 3) {{
        println("FAIL pre: ${{root.get_inner_n()}}")
        kotlin.system.exitProcess(1)
    }}
    val snap = root.save_state()
    val rest = Outer()
    rest.restore_state(snap)
    if (rest.get_inner_n() != 3) {{
        println("FAIL post: ${{rest.get_inner_n()}}")
        kotlin.system.exitProcess(1)
    }}
    println("PASS: {tag}")
}}
''',
    },
    "swift": {
        "target": "swift",
        "ext": "fswift",
        "blob_type": "String",
        "int_type": "Int",
        "self_": "self",
        "prologue": "",
        "epilogue": '''
let root = Outer()
root.tick()
root.tick()
root.tick()
if root.get_inner_n() != 3 {{
    print("FAIL pre: \\(root.get_inner_n())")
    exit(1)
}}
let snap = root.save_state()
let rest = Outer()
rest.restore_state(snap)
if rest.get_inner_n() != 3 {{
    print("FAIL post: \\(rest.get_inner_n())")
    exit(1)
}}
print("PASS: {tag}")
''',
    },
    "csharp": {
        "target": "csharp",
        "ext": "fcs",
        "blob_type": "string",
        "int_type": "int",
        "self_": "this",
        "prologue": "",
        "epilogue": '''
public class Program {{
    public static void Main() {{
        var root = new Outer();
        root.tick();
        root.tick();
        root.tick();
        if (root.get_inner_n() != 3) {{
            System.Console.WriteLine($"FAIL pre: {{root.get_inner_n()}}");
            System.Environment.Exit(1);
        }}
        var snap = root.save_state();
        var rest = new Outer();
        rest.restore_state(snap);
        if (rest.get_inner_n() != 3) {{
            System.Console.WriteLine($"FAIL post: {{rest.get_inner_n()}}");
            System.Environment.Exit(1);
        }}
        System.Console.WriteLine("PASS: {tag}");
    }}
}}
''',
    },
    "java": {
        "target": "java",
        "ext": "fjava",
        "blob_type": "String",
        "int_type": "int",
        "self_": "this",
        # Inner is package-private so Java's "one public class per
        # file" rule still allows Outer to be public.
        "inner_visibility": "private",
        "prologue": "",
        "epilogue": '''
class Main {{
    public static void main(String[] args) {{
        Outer root = new Outer();
        root.tick();
        root.tick();
        root.tick();
        if (root.get_inner_n() != 3) {{
            System.out.println("FAIL pre: " + root.get_inner_n());
            System.exit(1);
        }}
        String snap = root.save_state();
        Outer rest = new Outer();
        rest.restore_state(snap);
        if (rest.get_inner_n() != 3) {{
            System.out.println("FAIL post: " + rest.get_inner_n());
            System.exit(1);
        }}
        System.out.println("PASS: {tag}");
    }}
}}
''',
    },
    "go": {
        "target": "go",
        "ext": "fgo",
        "blob_type": "string",
        "int_type": "int",
        "self_": "s",
        "prologue": "package main\n\nimport (\n    \"fmt\"\n    \"os\"\n)\n\n",
        "epilogue": '''
func main() {{
    root := @@Outer()
    root.Tick()
    root.Tick()
    root.Tick()
    if root.Get_inner_n() != 3 {{
        fmt.Printf("FAIL pre: %d\\n", root.Get_inner_n())
        os.Exit(1)
    }}
    snap := root.Save_state()
    rest := @@Outer()
    rest.Restore_state(snap)
    if rest.Get_inner_n() != 3 {{
        fmt.Printf("FAIL post: %d\\n", rest.Get_inner_n())
        os.Exit(1)
    }}
    fmt.Println("PASS: {tag}")
}}
''',
    },
    # Erlang excluded — gen_statem processes don't compose as in-
    # process domain fields. Cross-system Erlang persist is covered
    # separately via the per-language test fixtures
    # (tests/erlang/multi/*).
    #
    # C / C++ / GDScript: separate driver shapes; the matrix harness
    # owns runtime exec for those. Frame source still renders per
    # this generator — they're just skipped at the runner script.
    "c": {
        "target": "c",
        "ext": "fc",
        "blob_type": "char*",
        "int_type": "int",
        "self_": "self",
        "prologue": "#include <stdio.h>\n#include <stdlib.h>\n\n",
        "epilogue": '''
int main() {{
    Outer* root = @@Outer();
    Outer_tick(root);
    Outer_tick(root);
    Outer_tick(root);
    if (Outer_get_inner_n(root) != 3) {{
        printf("FAIL pre: %d\\n", Outer_get_inner_n(root));
        Outer_destroy(root);
        return 1;
    }}
    char* snap = Outer_save_state(root);
    Outer* rest = @@Outer();
    Outer_restore_state(rest, snap);
    if (Outer_get_inner_n(rest) != 3) {{
        printf("FAIL post: %d\\n", Outer_get_inner_n(rest));
        Outer_destroy(root);
        Outer_destroy(rest);
        return 1;
    }}
    printf("PASS: {tag}\\n");
    Outer_destroy(root);
    Outer_destroy(rest);
    return 0;
}}
''',
    },
    "cpp": {
        "target": "cpp_17",
        "ext": "fcpp",
        "blob_type": "std::string",
        "int_type": "int",
        "self_": "this",
        "prologue": "#include <iostream>\n\n",
        "epilogue": '''
int main() {{
    Outer root;
    root.tick();
    root.tick();
    root.tick();
    if (root.get_inner_n() != 3) {{
        std::cout << "FAIL pre: " << root.get_inner_n() << std::endl;
        return 1;
    }}
    std::string snap = root.save_state();
    Outer rest;
    rest.restore_state(snap);
    if (rest.get_inner_n() != 3) {{
        std::cout << "FAIL post: " << rest.get_inner_n() << std::endl;
        return 1;
    }}
    std::cout << "PASS: {tag}" << std::endl;
    return 0;
}}
''',
    },
    "gdscript": {
        "target": "gdscript",
        "ext": "fgd",
        "blob_type": "String",
        "int_type": "int",
        "self_": "self",
        "prologue": "extends SceneTree\n\n",
        "epilogue": '''
func _init():
    var root = Outer.new()
    root.tick()
    root.tick()
    root.tick()
    if root.get_inner_n() != 3:
        print("FAIL pre: ", root.get_inner_n())
        quit(1)
        return
    var snap = root.save_state()
    var rest = Outer.new()
    rest.restore_state(snap)
    if rest.get_inner_n() != 3:
        print("FAIL post: ", rest.get_inner_n())
        quit(1)
        return
    print("PASS: {tag}")
    quit()
''',
    },
}


# JS / TS use camelCase method names; everything else uses snake_case.
def method_names_for(lang):
    if lang in ("javascript", "typescript"):
        return {
            "tick": "tick",
            "get_inner_n": "getInnerN",
            "get_n": "getN",
            "save": "saveState",
            "load": "restoreState",
        }
    if lang == "go":
        # Go capitalizes for export; in Frame source we keep
        # snake_case and emit native code in main.
        return {
            "tick": "tick",
            "get_inner_n": "get_inner_n",
            "get_n": "get_n",
            "save": "save_state",
            "load": "restore_state",
        }
    return {
        "tick": "tick",
        "get_inner_n": "get_inner_n",
        "get_n": "get_n",
        "save": "save_state",
        "load": "restore_state",
    }


def gen_p1(lang, case_id):
    """Render P1 simple_nested for `lang`."""
    spec = LANGS[lang]
    names = method_names_for(lang)
    tag = f"p1_simple_nested_{case_id}"
    self_ = spec["self_"]
    blob = spec["blob_type"]
    int_t = spec["int_type"]
    inner_vis = spec.get("inner_visibility", "")
    inner_decl = f"@@system {inner_vis} Inner" if inner_vis else "@@system Inner"

    # Frame skeleton — identical structure across backends; only
    # the receiver / type names vary.
    frame = f'''@@[target("{spec["target"]}")]

{spec["prologue"]}@@[persist({blob})]
@@[save({names["save"]})]
@@[load({names["load"]})]
{inner_decl} {{{{
    interface:
        {names["tick"]}()
        {names["get_n"]}(): {int_t}
    machine:
        $Active {{{{
            {names["tick"]}() {{{{ {self_}.n = {self_}.n + 1 }}}}
            {names["get_n"]}(): {int_t} {{{{ @@:({self_}.n) }}}}
        }}}}
    domain:
        n: {int_t} = 0
}}}}

@@[persist({blob})]
@@[save({names["save"]})]
@@[load({names["load"]})]
@@[main]
@@system Outer {{{{
    interface:
        {names["tick"]}()
        {names["get_inner_n"]}(): {int_t}
    machine:
        $Run {{{{
            {names["tick"]}() {{{{ {self_}.inner.{names["tick"]}() }}}}
            {names["get_inner_n"]}(): {int_t} {{{{ @@:({self_}.inner.{names["get_n"]}()) }}}}
        }}}}
    domain:
        inner: Inner = @@Inner()
}}}}
'''

    # The epilogue carries `{tag}` as a single literal — the inner
    # `{{` escaping is to keep the f-string above clean.
    return frame.format() + spec["epilogue"].format(tag=tag)


def write_cases(out_dir: Path, langs, max_per_pattern):
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for lang in langs:
        ext = LANGS[lang]["ext"]
        for i in range(max_per_pattern):
            case_id = f"{i:03d}"
            text = gen_p1(lang, case_id)
            tag = f"p1_simple_nested_{case_id}"
            out = out_dir / f"{lang}_{tag}.{ext}"
            out.write_text(text)
            written += 1
    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max", type=int, default=3,
                    help="Cases per pattern per language (default 3)")
    ap.add_argument("--langs", nargs="+",
                    default=sorted(LANGS.keys()),
                    help="Languages to generate (default: all 16; "
                         "Erlang is excluded by design)")
    ap.add_argument("--out-dir", type=Path,
                    default=Path("cases_persist_multisys"),
                    help="Output directory")
    args = ap.parse_args()

    n = write_cases(args.out_dir, args.langs, args.max)
    print(f"Wrote {n} cases to {args.out_dir}/ ({len(args.langs)} langs)")


if __name__ == "__main__":
    main()
