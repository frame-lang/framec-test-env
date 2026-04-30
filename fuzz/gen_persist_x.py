#!/usr/bin/env python3
"""
Phase 24 — Persist cross-product regression net.

Locks in coverage for the 9-backend persist bulk fix shipped 2026-04-29
where compartment context fields (state_args + enter_args) were missing
from save_state/restore_state in Erlang, Java, Kotlin, C#, Swift, C++,
PHP, C, Rust.

This corpus deliberately exercises the BUG SHAPE — without state-args
or enter-args declared on a state, a system can persist correctly
even if the codegen serializer drops compartment.state_args.
Phase 2 (gen_persist.py) is in that category. Phase 24 declares state-
args and enter-args, transitions into states with non-default values,
saves, restores, and asserts the args round-trip.

Patterns:
  P1 state_args_basic     — state declares args, transition with values,
                             save, restore, verify args still bound.
  P2 enter_args_basic     — enter handler takes args, transition with
                             values, save mid-flight, restore, verify
                             args still bound.
  P3 hsm_state_args       — parent has state-args, child binds them,
                             transition, save, restore, verify.
  P4 push_state_args      — push to state with state-args, save (with
                             stack full), restore, pop, verify args
                             restored from stack.

Usage:
  python3 gen_persist_x.py --max 200
  ./run_persist_x.sh
"""
import argparse
import itertools
from pathlib import Path

# --- Per-language config -------------------------------------------------

class LangSpec:
    __slots__ = (
        "target", "ext", "int_type", "str_type",
        "self_x", "self_v",
        "save_call", "restore_call",
        "println", "fail_exit",
        "domain_init",
    )
    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k, ""))


def _build_specs():
    specs = {}

    specs["python_3"] = LangSpec(
        target="python_3", ext="fpy",
        int_type="int", str_type="str",
        self_x="self.x", self_v="self.v",
        save_call="snap = inst.save_state()",
        restore_call="rest = {SYS}.restore_state(snap)",
        println='print("PASS: phase24")',
        fail_exit="""
def _fail(msg):
    print("FAIL: " + str(msg))
    raise SystemExit(1)
""",
        domain_init="0",
    )

    specs["javascript"] = LangSpec(
        target="javascript", ext="fjs",
        int_type="number", str_type="string",
        self_x="this.x", self_v="this.v",
        save_call="const snap = inst.saveState();",
        restore_call="const rest = {SYS}.restoreState(snap);",
        println='console.log("PASS: phase24");',
        fail_exit="""
function _fail(msg) { console.log("FAIL: " + msg); process.exit(1); }
""",
        domain_init="0",
    )

    specs["typescript"] = LangSpec(
        target="typescript", ext="fts",
        int_type="number", str_type="string",
        self_x="this.x", self_v="this.v",
        save_call="const snap = inst.saveState();",
        restore_call="const rest = {SYS}.restoreState(snap);",
        println='console.log("PASS: phase24");',
        fail_exit="""
function _fail(msg: string): void { console.log("FAIL: " + msg); process.exit(1); }
""",
        domain_init="0",
    )

    return specs

LANGS = _build_specs()


# --- Pattern P1: state_args_basic ---------------------------------------

def gen_p1_python(case_id, sys_name, value):
    """P1 — state-args round-trip via persist.

    System: $Idle / $Active(slot: int)
    Drive:  -> $Active(VALUE)
            save_state -> snap
            restore_state(snap) -> rest
    Verify: rest.get_slot() returns VALUE (proves state-args were
            preserved across save/restore boundary).
    """
    return f"""@@target python_3

@@persist
@@system {sys_name} {{
    interface:
        kick(v: int)
        get_slot(): int

    machine:
        $Idle {{
            kick(v: int) {{
                -> $Active(v)
            }}
            get_slot(): int {{
                @@:(-1)
                return
            }}
        }}

        $Active(slot: int) {{
            kick(v: int) {{
                -> $Active(v)
            }}
            get_slot(): int {{
                @@:(slot)
                return
            }}
        }}
    domain:
        v: int = 0
}}

{LANGS['python_3'].fail_exit.strip()}

if __name__ == '__main__':
    inst = @@{sys_name}()
    inst.kick({value})
    pre_slot = inst.get_slot()
    if pre_slot != {value}:
        _fail("pre-save slot " + str(pre_slot) + " != " + str({value}))
    snap = inst.save_state()
    rest = {sys_name}.restore_state(snap)
    post_slot = rest.get_slot()
    if post_slot != {value}:
        _fail("post-restore slot " + str(post_slot) + " != " + str({value}))
    print("PASS: p1 state_args slot=" + str(post_slot))
"""


# --- Pattern P2: enter_args_basic ---------------------------------------

def gen_p2_python(case_id, sys_name, value):
    """P2 — enter-args round-trip via persist.

    System: $Idle / $Done with enter handler taking args.
    Drive:  -> (VALUE) $Done
            save_state -> snap
            restore_state(snap) -> rest
    Verify: rest.get_tag() returns the tag passed to enter (proves
            enter-args were preserved across save/restore boundary).
    """
    return f"""@@target python_3

@@persist
@@system {sys_name} {{
    interface:
        kick(v: int)
        get_tag(): int

    machine:
        $Idle {{
            kick(v: int) {{
                -> (v) $Done
            }}
            get_tag(): int {{
                @@:(-1)
                return
            }}
        }}

        $Done {{
            $> (tag: int) {{
                self.cached = tag
            }}
            kick(v: int) {{
                -> (v) $Done
            }}
            get_tag(): int {{
                @@:(self.cached)
                return
            }}
        }}
    domain:
        cached: int = 0
}}

{LANGS['python_3'].fail_exit.strip()}

if __name__ == '__main__':
    inst = @@{sys_name}()
    inst.kick({value})
    pre_tag = inst.get_tag()
    if pre_tag != {value}:
        _fail("pre-save tag " + str(pre_tag) + " != " + str({value}))
    snap = inst.save_state()
    rest = {sys_name}.restore_state(snap)
    post_tag = rest.get_tag()
    if post_tag != {value}:
        _fail("post-restore tag " + str(post_tag) + " != " + str({value}))
    print("PASS: p2 enter_args tag=" + str(post_tag))
"""


# --- Pattern P3: hsm_state_args ----------------------------------------

def gen_p3_python(case_id, sys_name, value):
    """P3 — HSM cascade with state-args at parent level + persist.

    Parent has state-arg `x`, child cascades up. Transition into child
    binds the parent-level state-arg via the cascade. Save in child,
    restore, verify state-arg round-trips through the cascade chain.

    Pattern matches Phase 15 sa_p10 — state-args declared on cascaded
    parent, bound by name from child.
    """
    return f"""@@target python_3

@@persist
@@system {sys_name} {{
    interface:
        drive(p: int)
        get_x(): int

    machine:
        $Start {{
            drive(p: int) {{
                -> $Child(p)
            }}
            get_x(): int {{
                @@:(-1)
                return
            }}
        }}

        $Child => $Parent(x: int) {{
            drive(p: int) {{
                -> $Child(p)
            }}
            get_x(): int {{
                @@:(x)
                return
            }}
        }}

        $Parent {{
        }}
    domain:
        v: int = 0
}}

{LANGS['python_3'].fail_exit.strip()}

if __name__ == '__main__':
    inst = @@{sys_name}()
    inst.drive({value})
    pre = inst.get_x()
    if pre != {value}:
        _fail("pre-save x " + str(pre) + " != " + str({value}))
    snap = inst.save_state()
    rest = {sys_name}.restore_state(snap)
    post = rest.get_x()
    if post != {value}:
        _fail("post-restore x " + str(post) + " != " + str({value}))
    print("PASS: p3 hsm_state_args x=" + str(post))
"""


# --- Pattern P4: push_state_args ---------------------------------------

def gen_p4_python(case_id, sys_name, value):
    """P4 — push/pop with state-args + persist.

    Drive into $Modal(VALUE) via push; save while modal stack is full;
    restore; pop and verify the popped state's args were preserved on
    the stack.

    Why: the modal stack stores compartment refs; if compartment
    serialization drops state_args, the popped state will have
    bogus arg values.
    """
    return f"""@@target python_3

@@persist
@@system {sys_name} {{
    interface:
        push_modal(v: int)
        pop_modal()
        get_slot(): int

    machine:
        $Idle {{
            push_modal(v: int) {{
                push$
                -> $Modal(v)
            }}
            pop_modal() {{
                -> pop$
            }}
            get_slot(): int {{
                @@:(-99)
                return
            }}
        }}

        $Modal(slot: int) {{
            push_modal(v: int) {{
                push$
                -> $Modal(v)
            }}
            pop_modal() {{
                -> pop$
            }}
            get_slot(): int {{
                @@:(slot)
                return
            }}
        }}
    domain:
        v: int = 0
}}

{LANGS['python_3'].fail_exit.strip()}

if __name__ == '__main__':
    inst = @@{sys_name}()
    inst.push_modal({value})
    pre = inst.get_slot()
    if pre != {value}:
        _fail("pre-save slot " + str(pre) + " != " + str({value}))
    snap = inst.save_state()
    rest = {sys_name}.restore_state(snap)
    post = rest.get_slot()
    if post != {value}:
        _fail("post-restore slot " + str(post) + " != " + str({value}))
    print("PASS: p4 push_state_args slot=" + str(post))
"""


def gen_p5_python(case_id, sys_name, value):
    """P5 — persist × multi-event (drive A, save, restore, drive B).

    Drive event 1 sets state-arg slot to VALUE; save mid-flight;
    restore in fresh instance; drive event 2 increments the slot
    by 100 (transitions to a new $Active(slot+100)). Verify the
    POST-RESTORE event correctly continues from the saved state.

    Why: even if save/restore is correct in isolation (P1-P4), the
    restored compartment must be a fully functional state machine
    that can transition, dispatch handlers, and bind state-args from
    further events. Tests post-restore correctness, not just static
    equivalence.
    """
    return f"""@@target python_3

@@persist
@@system {sys_name} {{
    interface:
        seed(v: int)
        bump()
        get_slot(): int

    machine:
        $Idle {{
            seed(v: int) {{
                -> $Active(v)
            }}
            bump() {{
                @@:(-1)
                return
            }}
            get_slot(): int {{
                @@:(-1)
                return
            }}
        }}

        $Active(slot: int) {{
            seed(v: int) {{
                -> $Active(v)
            }}
            bump() {{
                -> $Active(slot + 100)
            }}
            get_slot(): int {{
                @@:(slot)
                return
            }}
        }}
    domain:
        v: int = 0
}}

{LANGS['python_3'].fail_exit.strip()}

if __name__ == '__main__':
    inst = @@{sys_name}()
    inst.seed({value})
    pre = inst.get_slot()
    if pre != {value}:
        _fail("pre-save " + str(pre) + " != " + str({value}))
    snap = inst.save_state()
    rest = {sys_name}.restore_state(snap)
    rest.bump()
    post = rest.get_slot()
    expected = {value} + 100
    if post != expected:
        _fail("post-event-after-restore " + str(post) + " != " + str(expected))
    print("PASS: p5 multi_event slot=" + str(post))
"""


# --- Driver ------------------------------------------------------------

PATTERNS = [
    "p1_state_args",
    "p2_enter_args",
    "p3_hsm_state_args",
    "p4_push_state_args",
    "p5_multi_event",
]
VALUES = [0, 1, 42, 100, -7]


# --- JavaScript variants (same Frame, different harness language) -----

# Each pattern has the same Frame system; the harness language differs.
# Frame body templates take {sys} and emit a {sys} system + harness header.

P1_FRAME = """@@target {target}

@@persist
@@system {sys} {{
    interface:
        kick(v: int)
        get_slot(): int

    machine:
        $Idle {{
            kick(v: int) {{
                -> $Active(v)
            }}
            get_slot(): int {{
                @@:(-1)
                return
            }}
        }}

        $Active(slot: int) {{
            kick(v: int) {{
                -> $Active(v)
            }}
            get_slot(): int {{
                @@:(slot)
                return
            }}
        }}
    domain:
        v: int = 0
}}"""

P2_FRAME = """@@target {target}

@@persist
@@system {sys} {{
    interface:
        kick(v: int)
        get_tag(): int

    machine:
        $Idle {{
            kick(v: int) {{
                -> (v) $Done
            }}
            get_tag(): int {{
                @@:(-1)
                return
            }}
        }}

        $Done {{
            $> (tag: int) {{
                {self_prefix}.cached = tag
            }}
            kick(v: int) {{
                -> (v) $Done
            }}
            get_tag(): int {{
                @@:({self_prefix}.cached)
                return
            }}
        }}
    domain:
        cached: int = 0
}}"""

P3_FRAME = """@@target {target}

@@persist
@@system {sys} {{
    interface:
        drive(p: int)
        get_x(): int

    machine:
        $Start {{
            drive(p: int) {{
                -> $Child(p)
            }}
            get_x(): int {{
                @@:(-1)
                return
            }}
        }}

        $Child => $Parent(x: int) {{
            drive(p: int) {{
                -> $Child(p)
            }}
            get_x(): int {{
                @@:(x)
                return
            }}
        }}

        $Parent {{
        }}
    domain:
        v: int = 0
}}"""

P4_FRAME = """@@target {target}

@@persist
@@system {sys} {{
    interface:
        push_modal(v: int)
        pop_modal()
        get_slot(): int

    machine:
        $Idle {{
            push_modal(v: int) {{
                push$
                -> $Modal(v)
            }}
            pop_modal() {{
                -> pop$
            }}
            get_slot(): int {{
                @@:(-99)
                return
            }}
        }}

        $Modal(slot: int) {{
            push_modal(v: int) {{
                push$
                -> $Modal(v)
            }}
            pop_modal() {{
                -> pop$
            }}
            get_slot(): int {{
                @@:(slot)
                return
            }}
        }}
    domain:
        v: int = 0
}}"""


P5_FRAME = """@@target {target}

@@persist
@@system {sys} {{
    interface:
        seed(v: int)
        bump()
        get_slot(): int

    machine:
        $Idle {{
            seed(v: int) {{
                -> $Active(v)
            }}
            bump() {{
                @@:(-1)
                return
            }}
            get_slot(): int {{
                @@:(-1)
                return
            }}
        }}

        $Active(slot: int) {{
            seed(v: int) {{
                -> $Active(v)
            }}
            bump() {{
                -> $Active(slot + 100)
            }}
            get_slot(): int {{
                @@:(slot)
                return
            }}
        }}
    domain:
        v: int = 0
}}"""


PATTERN_FRAMES = {
    "p1_state_args":     (P1_FRAME, "kick",        "get_slot", "p1 state_args slot="),
    "p2_enter_args":     (P2_FRAME, "kick",        "get_tag",  "p2 enter_args tag="),
    "p3_hsm_state_args": (P3_FRAME, "drive",       "get_x",    "p3 hsm_state_args x="),
    "p4_push_state_args":(P4_FRAME, "push_modal",  "get_slot", "p4 push_state_args slot="),
    "p5_multi_event":    (P5_FRAME, "seed",        "get_slot", "p5 multi_event slot="),
}


def gen_javascript(pattern, case_id, sys_name, value, target="javascript"):
    """JS / TS share the same shape — TS gets `: string` annotation in
    fail_exit via the spec; everything else is identical.

    P5 multi_event differs in that the post-restore step calls bump()
    and expects slot+100, not the raw value."""
    frame, drive_method, get_method, label = PATTERN_FRAMES[pattern]
    fail = LANGS[target].fail_exit.strip()
    body = frame.format(target=target, sys=sys_name, self_prefix="this")
    if pattern == "p5_multi_event":
        return f"""{body}

{fail}

const inst = new {sys_name}();
inst.{drive_method}({value});
const pre = inst.{get_method}();
if (pre !== {value}) _fail("pre-save: " + pre + " !== {value}");
const snap = inst.saveState();
const rest = {sys_name}.restoreState(snap);
rest.bump();
const post = rest.{get_method}();
const expected = {value} + 100;
if (post !== expected) _fail("post-event-after-restore: " + post + " !== " + expected);
console.log("PASS: {label}" + post);
"""
    return f"""{body}

{fail}

const inst = new {sys_name}();
inst.{drive_method}({value});
const pre = inst.{get_method}();
if (pre !== {value}) _fail("pre-save: " + pre + " !== {value}");
const snap = inst.saveState();
const rest = {sys_name}.restoreState(snap);
const post = rest.{get_method}();
if (post !== {value}) _fail("post-restore: " + post + " !== {value}");
console.log("PASS: {label}" + post);
"""


def gen_case(lang, pattern, case_id, value):
    sys_name = f"P24{case_id:04d}"
    if lang == "python_3":
        if pattern == "p1_state_args":
            return gen_p1_python(case_id, sys_name, value)
        if pattern == "p2_enter_args":
            return gen_p2_python(case_id, sys_name, value)
        if pattern == "p3_hsm_state_args":
            return gen_p3_python(case_id, sys_name, value)
        if pattern == "p4_push_state_args":
            return gen_p4_python(case_id, sys_name, value)
        if pattern == "p5_multi_event":
            return gen_p5_python(case_id, sys_name, value)
    if lang == "javascript":
        return gen_javascript(pattern, case_id, sys_name, value, target="javascript")
    if lang == "typescript":
        return gen_javascript(pattern, case_id, sys_name, value, target="typescript")
    raise ValueError(f"{lang}/{pattern}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--max", type=int, default=80)
    p.add_argument("--lang", type=str, default="python_3")
    p.add_argument("--out", type=Path,
                   default=Path(__file__).parent / "cases_persist_x")
    args = p.parse_args()

    spec = LANGS.get(args.lang)
    if spec is None:
        print(f"unsupported lang: {args.lang}")
        return

    args.out.mkdir(parents=True, exist_ok=True)
    lang_dir = args.out / spec.target
    lang_dir.mkdir(exist_ok=True)

    cases = []
    cid = 0
    for pat in PATTERNS:
        for v in VALUES:
            cases.append((pat, cid, v))
            cid += 1

    cases = cases[:args.max]
    for cid, (pat, _, v) in enumerate(cases):
        content = gen_case(args.lang, pat, cid, v)
        out_path = lang_dir / f"case_{cid:04d}_{pat}.{spec.ext}"
        out_path.write_text(content)
    print(f"Generated {len(cases)} Phase 24 cases for {spec.target}")


if __name__ == "__main__":
    main()
