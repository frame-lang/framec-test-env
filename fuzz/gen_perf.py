#!/usr/bin/env python3
"""
Phase 18 — perf + endurance fuzz (Wave 2).

Replaces wave-1's unrolled drivers (N capped at 100) with language-
native loops + timing instrumentation. Each driver:
  1. Records start time (high-resolution monotonic clock per lang).
  2. Loops N times invoking the dispatch / transition / push-pop
     handler.
  3. Records end time, computes elapsed-ms.
  4. Prints `PERF: pattern=<p> lang=<l> n=<N> ms=<elapsed> result=<r>`
     before the PASS line. Runner / aggregator can grep PERF lines.
  5. Verifies the count matches N.

Wave 2 tiers:
  smoke: N = 100        (correctness sanity, fast)
  core:  N = 10_000     (default useful run)
  full:  N = 1_000_000  (real stress; slow backends take seconds)

Patterns (3, same as wave 1):
  P1 many_dispatches   — bump() N times. Event-dispatch loop.
  P2 transition_pingpong — alternating $S0↔$S1 transitions, N cycles.
  P3 push_pop_depth    — push$ N times, pop$ N times.

Total: 3 patterns × 3 tiers × 17 backends = 153 case-runs full.

Usage:
    python3 gen_perf.py
    ./run_perf.sh --tier=smoke    # N=100
    ./run_perf.sh --tier=core     # N=10000
    ./run_perf.sh --tier=full     # N=1000000
"""
from pathlib import Path

from gen_nested import LANGS, method_name


# Tier → N. Capped at 1M because Frame interpreted backends
# (Python/Ruby/Lua/Erlang) take 5-30s per pattern at 1M; further
# scaling needs OS-level mem instrumentation we don't have.
TIER_N = {"smoke": 100, "core": 10_000, "full": 1_000_000}


class Pattern:
    __slots__ = ("name", "build_states", "loop_method", "compute")

    def __init__(self, name, build_states, loop_method, compute):
        self.name = name
        self.build_states = build_states
        self.loop_method = loop_method  # method to call N times in the loop
        self.compute = compute  # lambda(N) -> int


def _build_p1_many_dispatches(spec, lang):
    m_bump = method_name(lang, "bump")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_bump}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + 1{spec.stmt_end}",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


def _build_p2_transition_pingpong(spec, lang):
    m_drive = method_name(lang, "drive")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_drive}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + 1{spec.stmt_end}",
        f"                -> $S1",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
        f"        $S1 {{",
        f"            {m_drive}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + 1{spec.stmt_end}",
        f"                -> $S0",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
    ]


def _build_p3_push_pop_depth(spec, lang):
    m_push = method_name(lang, "push_then")
    m_pop = method_name(lang, "go_back")
    m_get = method_name(lang, "get_f")
    return [
        f"        $S0 {{",
        f"            {m_push}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + 1{spec.stmt_end}",
        f"                push$",
        f"                -> $S1",
        f"            }}",
        f"            {m_pop}() {{",
        f"                -> pop$",
        f"            }}",
        f"            {m_get}(): int {{ @@:({spec.self_word}{spec.field_op}f) }}",
        f"        }}",
        f"        $S1 {{",
        f"            {m_push}() {{",
        f"                {spec.self_word}{spec.field_op}f = {spec.self_word}{spec.field_op}f + 1{spec.stmt_end}",
        f"                push$",
        f"                -> $S0",
        f"            }}",
        f"            {m_pop}() {{",
        f"                -> pop$",
        f"            }}",
        f"        }}",
    ]


PATTERNS = [
    Pattern("p1_many_dispatches",
            _build_p1_many_dispatches,
            "bump",
            lambda n: n),
    Pattern("p2_transition_pingpong",
            _build_p2_transition_pingpong,
            "drive",
            lambda n: n),
    Pattern("p3_push_pop_depth",
            _build_p3_push_pop_depth,
            None,  # P3 is a paired loop: push N times, then pop N times
            lambda n: n),
]


def case_id(pattern, tier):
    return f"perf_{pattern.name}__{tier}"


def equiv_class(pattern):
    return pattern.name


def enumerate_cases():
    """One case per pattern × tier. Tier name selects N."""
    seen = set()
    for pattern in PATTERNS:
        for tier_name in TIER_N:
            cid = case_id(pattern, tier_name)
            cls = equiv_class(pattern)
            is_smoke = (tier_name == "smoke")
            n = TIER_N[tier_name]
            expected = pattern.compute(n)
            yield (cid, cls, expected, pattern, tier_name, n, is_smoke)


def _emit_perf_line(lang: str, pattern_name: str, n_var: str,
                    elapsed_var: str, result_var: str) -> str:
    """Per-language PERF-line print. Format:
       PERF: pattern=<p> lang=<l> n=<N> ms=<elapsed> result=<r>
    Aggregator parses PERF lines from stdout."""
    fmt = f"PERF: pattern={pattern_name} lang={lang} n="
    if lang == "python_3":
        return f'print(f"{fmt}{{{n_var}}} ms={{{elapsed_var}:.2f}} result={{{result_var}}}")'
    if lang == "javascript":
        return f'console.log("{fmt}" + {n_var} + " ms=" + {elapsed_var}.toFixed(2) + " result=" + {result_var});'
    if lang == "typescript":
        return f'console.log("{fmt}" + {n_var} + " ms=" + {elapsed_var}.toFixed(2) + " result=" + {result_var});'
    if lang == "ruby":
        return f'puts("{fmt}#{{{n_var}}} ms=#{{format(\'%.2f\', {elapsed_var})}} result=#{{{result_var}}}")'
    if lang == "lua":
        return f'print(string.format("{fmt}%d ms=%.2f result=%d", {n_var}, {elapsed_var}, {result_var}))'
    if lang == "php":
        return f'printf("{fmt}%d ms=%.2f result=%d\\n", {n_var}, {elapsed_var}, {result_var});'
    if lang == "dart":
        return f'print("{fmt}$' + n_var + ' ms=${' + elapsed_var + '.toStringAsFixed(2)} result=$' + result_var + '");'
    if lang == "rust":
        return f'println!("{fmt}{{}} ms={{:.2}} result={{}}", {n_var}, {elapsed_var}, {result_var});'
    if lang == "go":
        return f'fmt.Printf("{fmt}%d ms=%.2f result=%d\\n", {n_var}, {elapsed_var}, {result_var})'
    if lang == "swift":
        # Swift can't easily nest String(format:) inside interpolation
        # without escaping quotes which fails in some contexts. Just
        # print the raw double — parser can round.
        return f'print("{fmt}\\({n_var}) ms=\\({elapsed_var}) result=\\({result_var})")'
    if lang == "java":
        return f'System.out.printf("{fmt}%d ms=%.2f result=%d%n", {n_var}, {elapsed_var}, {result_var});'
    if lang == "kotlin":
        return f'println("{fmt}$' + n_var + ' ms=${"%.2f".format(' + elapsed_var + ')} result=$' + result_var + '")'
    if lang == "csharp":
        return f'System.Console.WriteLine($"{fmt}{{{n_var}}} ms={{{elapsed_var}:F2}} result={{{result_var}}}");'
    if lang == "c":
        return f'printf("{fmt}%d ms=%.2f result=%d\\n", {n_var}, {elapsed_var}, {result_var});'
    if lang == "cpp":
        return f'std::cout << "{fmt}" << {n_var} << " ms=" << {elapsed_var} << " result=" << {result_var} << std::endl;'
    if lang == "gdscript":
        return f'print("{fmt}" + str({n_var}) + " ms=" + str({elapsed_var}) + " result=" + str({result_var}))'
    return ""


def gen_case(lang, cid, equiv, expected, pattern, tier_name, n, is_smoke):
    spec = LANGS[lang]
    sys_name = f"Perf_{cid}"

    m_get_f = method_name(lang, "get_f")
    verify = m_get_f
    loop_m = pattern.loop_method  # may be None for P3
    is_p3 = pattern.name == "p3_push_pop_depth"

    state_lines = pattern.build_states(spec, lang)

    # Interface: union of methods used.
    interface_methods = set()
    if is_p3:
        interface_methods.add(method_name(lang, "push_then"))
        interface_methods.add(method_name(lang, "go_back"))
    elif loop_m:
        interface_methods.add(method_name(lang, loop_m))
    interface_methods.add(verify)

    lines = []
    lines.append(f"@@target {spec.target}")
    if lang == "php":
        lines.append("<?php")
    lines.append("")
    if lang == "erlang":
        lines.append(f"%% FUZZ_EXPECTED_N: {expected}")
        lines.append(f"%% FUZZ_EQUIV_CLASS: {equiv}")
        lines.append(f"%% FUZZ_SMOKE: {'yes' if is_smoke else 'no'}")
        lines.append(f"%% FUZZ_VERIFY_METHOD: {verify}")
        lines.append(f"%% FUZZ_LOOP_N: {n}")
        if is_p3:
            lines.append(f"%% FUZZ_LOOP_METHOD: push_pop")
            lines.append(f"%% FUZZ_PUSH_METHOD: {method_name(lang, 'push_then')}")
            lines.append(f"%% FUZZ_POP_METHOD: {method_name(lang, 'go_back')}")
        else:
            lines.append(f"%% FUZZ_LOOP_METHOD: {method_name(lang, loop_m)}")
        lines.append(f"%% FUZZ_PATTERN: {pattern.name}")
    lines.append("")
    lines.append(f"@@system {sys_name} {{")
    lines.append("    interface:")
    for m in sorted(interface_methods):
        if m == verify:
            lines.append(f"        {m}(): int")
        else:
            lines.append(f"        {m}()")
    lines.append("")
    lines.append("    machine:")
    lines.extend(state_lines)
    lines.append("")
    lines.append("    domain:")
    lines.append(f"        f: int = 0")
    lines.append("}")
    lines.append("")

    perf_str = pattern.name

    # Per-language driver with timing + native loop. Erlang driver
    # is generated by the runner from FUZZ_LOOP_* metadata.
    if lang == "python_3":
        lines.append(spec.fail_exit_def)
        lines.append("import time")
        lines.append(f"_inst = {sys_name}()")
        lines.append(f"_n = {n}")
        lines.append("_start = time.perf_counter()")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"for _ in range(_n):")
            lines.append(f"    _inst.{push_m}()")
            lines.append(f"for _ in range(_n):")
            lines.append(f"    _inst.{pop_m}()")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"for _ in range(_n):")
            lines.append(f"    _inst.{m_loop}()")
        lines.append("_elapsed_ms = (time.perf_counter() - _start) * 1000.0")
        lines.append(f"_ret = _inst.{verify}()")
        lines.append(_emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"if _ret != {expected}:")
        lines.append(f"    _fail(f\"expected ret={expected}, got {{_ret}}\")")
        lines.append(spec.println_pass.replace("nested-frame", "perf"))

    elif lang == "javascript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        lines.append(f"const _n = {n};")
        lines.append("const _start = process.hrtime.bigint();")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"for (let i = 0; i < _n; i++) _inst.{push_m}();")
            lines.append(f"for (let i = 0; i < _n; i++) _inst.{pop_m}();")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"for (let i = 0; i < _n; i++) _inst.{m_loop}();")
        lines.append("const _elapsed_ms = Number(process.hrtime.bigint() - _start) / 1e6;")
        lines.append(f"const _ret = _inst.{verify}();")
        lines.append(_emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "perf"))

    elif lang == "typescript":
        lines.append(spec.fail_exit_def)
        lines.append(f"const _inst = new {sys_name}();")
        lines.append(f"const _n: number = {n};")
        lines.append("const _start: bigint = process.hrtime.bigint();")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"for (let i = 0; i < _n; i++) _inst.{push_m}();")
            lines.append(f"for (let i = 0; i < _n; i++) _inst.{pop_m}();")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"for (let i = 0; i < _n; i++) _inst.{m_loop}();")
        lines.append("const _elapsed_ms: number = Number(process.hrtime.bigint() - _start) / 1e6;")
        lines.append(f"const _ret: number = _inst.{verify}();")
        lines.append(_emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"if (_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" + _ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "perf"))

    elif lang == "ruby":
        lines.append(spec.fail_exit_def)
        lines.append(f"_inst = {sys_name}.new")
        lines.append(f"_n = {n}")
        lines.append("_start = Process.clock_gettime(Process::CLOCK_MONOTONIC)")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"_n.times {{ _inst.{push_m} }}")
            lines.append(f"_n.times {{ _inst.{pop_m} }}")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"_n.times {{ _inst.{m_loop} }}")
        lines.append("_elapsed_ms = (Process.clock_gettime(Process::CLOCK_MONOTONIC) - _start) * 1000.0")
        lines.append(f"_ret = _inst.{verify}")
        lines.append(_emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"_fail(\"expected ret={expected}, got #{{_ret}}\") unless _ret == {expected}")
        lines.append(spec.println_pass.replace("nested-frame", "perf"))

    elif lang == "lua":
        lines.append(spec.fail_exit_def)
        lines.append(f"local _inst = {sys_name}.new()")
        lines.append(f"local _n = {n}")
        lines.append("local _start = os.clock()")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"for _ = 1, _n do _inst:{push_m}() end")
            lines.append(f"for _ = 1, _n do _inst:{pop_m}() end")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"for _ = 1, _n do _inst:{m_loop}() end")
        lines.append("local _elapsed_ms = (os.clock() - _start) * 1000.0")
        lines.append(f"local _ret = _inst:{verify}()")
        lines.append(_emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"if _ret ~= {expected} then _fail(\"expected ret={expected}, got \" .. tostring(_ret)) end")
        lines.append(spec.println_pass.replace("nested-frame", "perf"))

    elif lang == "php":
        lines.append(spec.fail_exit_def)
        lines.append(f"$_inst = new {sys_name}();")
        lines.append(f"$_n = {n};")
        lines.append("$_start = microtime(true);")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"for ($i = 0; $i < $_n; $i++) $_inst->{push_m}();")
            lines.append(f"for ($i = 0; $i < $_n; $i++) $_inst->{pop_m}();")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"for ($i = 0; $i < $_n; $i++) $_inst->{m_loop}();")
        lines.append("$_elapsed_ms = (microtime(true) - $_start) * 1000.0;")
        lines.append(f"$_ret = $_inst->{verify}();")
        lines.append(_emit_perf_line(lang, perf_str, "$_n", "$_elapsed_ms", "$_ret"))
        lines.append(f"if ($_ret !== {expected}) {{ _fail(\"expected ret={expected}, got \" . $_ret); }}")
        lines.append(spec.println_pass.replace("nested-frame", "perf"))

    elif lang == "dart":
        lines.append(spec.fail_exit_def)
        lines.append("void main() {")
        lines.append(f"    final _inst = {sys_name}();")
        lines.append(f"    final _n = {n};")
        lines.append("    final _sw = Stopwatch()..start();")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"    for (var i = 0; i < _n; i++) _inst.{push_m}();")
            lines.append(f"    for (var i = 0; i < _n; i++) _inst.{pop_m}();")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"    for (var i = 0; i < _n; i++) _inst.{m_loop}();")
        lines.append("    _sw.stop();")
        lines.append("    final _elapsed_ms = _sw.elapsedMicroseconds / 1000.0;")
        lines.append(f"    final _ret = _inst.{verify}();")
        lines.append("    " + _emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\"); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perf')}")
        lines.append("}")

    elif lang == "rust":
        lines.append(spec.fail_exit_def)
        lines.append("fn main() {")
        lines.append(f"    let mut _inst = {sys_name}::new();")
        lines.append(f"    let _n: i64 = {n};")
        lines.append("    let _start = std::time::Instant::now();")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"    for _ in 0.._n {{ _inst.{push_m}(); }}")
            lines.append(f"    for _ in 0.._n {{ _inst.{pop_m}(); }}")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"    for _ in 0.._n {{ _inst.{m_loop}(); }}")
        lines.append("    let _elapsed_ms = _start.elapsed().as_secs_f64() * 1000.0;")
        lines.append(f"    let _ret = _inst.{verify}();")
        lines.append("    " + _emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"    if _ret != {expected} {{ _fail(&format!(\"expected ret={expected}, got {{}}\", _ret)); }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perf')}")
        lines.append("}")

    elif lang == "go":
        lines.insert(2, "package main")
        lines.insert(3, "")
        lines.insert(4, 'import "fmt"')
        lines.insert(5, 'import "os"')
        lines.insert(6, 'import "time"')
        lines.insert(7, "")
        lines.append(spec.fail_exit_def)
        lines.append("func main() {")
        lines.append(f"    sm := New{sys_name}()")
        lines.append(f"    n := {n}")
        lines.append("    start := time.Now()")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            push_pasc = push_m[:1].upper() + push_m[1:]
            pop_pasc = pop_m[:1].upper() + pop_m[1:]
            lines.append(f"    for i := 0; i < n; i++ {{ sm.{push_pasc}() }}")
            lines.append(f"    for i := 0; i < n; i++ {{ sm.{pop_pasc}() }}")
        else:
            m_loop = method_name(lang, loop_m)
            method_pasc = m_loop[:1].upper() + m_loop[1:]
            lines.append(f"    for i := 0; i < n; i++ {{ sm.{method_pasc}() }}")
        lines.append("    elapsedMs := float64(time.Since(start).Microseconds()) / 1000.0")
        verify_pasc = verify[:1].upper() + verify[1:]
        lines.append(f"    ret := sm.{verify_pasc}()")
        lines.append("    " + _emit_perf_line(lang, perf_str, "n", "elapsedMs", "ret"))
        lines.append(f"    if ret != {expected} {{ _fail(fmt.Sprintf(\"expected ret={expected}, got %d\", ret)) }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perf')}")
        lines.append("}")

    elif lang == "swift":
        lines.append("import Foundation")
        lines.append(spec.fail_exit_def)
        lines.append(f"let _inst = {sys_name}()")
        lines.append(f"let _n = {n}")
        lines.append("let _start = Date()")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"for _ in 0..<_n {{ _inst.{push_m}() }}")
            lines.append(f"for _ in 0..<_n {{ _inst.{pop_m}() }}")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"for _ in 0..<_n {{ _inst.{m_loop}() }}")
        lines.append("let _elapsed_ms = Date().timeIntervalSince(_start) * 1000.0")
        lines.append(f"let _ret = _inst.{verify}()")
        lines.append(_emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"if _ret != {expected} {{ _fail(\"expected ret={expected}, got \\(_ret)\") }}")
        lines.append(spec.println_pass.replace("nested-frame", "perf"))

    elif lang == "java":
        lines.append("class Driver {")
        lines.append("    public static void main(String[] args) {")
        lines.append(f"        var _inst = new {sys_name}();")
        lines.append(f"        int _n = {n};")
        lines.append("        long _start = System.nanoTime();")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"        for (int i = 0; i < _n; i++) _inst.{push_m}();")
            lines.append(f"        for (int i = 0; i < _n; i++) _inst.{pop_m}();")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"        for (int i = 0; i < _n; i++) _inst.{m_loop}();")
        lines.append("        double _elapsed_ms = (System.nanoTime() - _start) / 1e6;")
        lines.append(f"        int _ret = (int) _inst.{verify}();")
        lines.append("        " + _emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"        if (_ret != {expected}) {{")
        lines.append(f"            System.out.println(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            System.exit(1);")
        lines.append(f"        }}")
        lines.append(f"        {spec.println_pass.replace('nested-frame', 'perf')}")
        lines.append("    }")
        lines.append("}")

    elif lang == "kotlin":
        lines.insert(1, f"@file:JvmName(\"Driver\")")
        lines.insert(2, f"package nf_{cid}")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("fun main() {")
        lines.append(f"    val _inst = {sys_name}()")
        lines.append(f"    val _n = {n}")
        lines.append("    val _start = System.nanoTime()")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"    for (i in 0 until _n) _inst.{push_m}()")
            lines.append(f"    for (i in 0 until _n) _inst.{pop_m}()")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"    for (i in 0 until _n) _inst.{m_loop}()")
        lines.append("    val _elapsed_ms = (System.nanoTime() - _start) / 1e6")
        lines.append(f"    val _ret = _inst.{verify}() as Int")
        lines.append("    " + _emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"    if (_ret != {expected}) {{ _fail(\"expected ret={expected}, got $_ret\") }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perf')}")
        lines.append("}")

    elif lang == "csharp":
        # `using` must be at file top, before `namespace`. Insert
        # near the @@target line so the system+namespace come after.
        lines.insert(2, "using System.Diagnostics;")
        lines.append(f"namespace nf_{cid} {{")
        lines.append("    public class Driver {")
        lines.append("        public static void Main() {")
        lines.append(f"            var _inst = new {sys_name}();")
        lines.append(f"            int _n = {n};")
        lines.append("            var _sw = Stopwatch.StartNew();")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"            for (int i = 0; i < _n; i++) _inst.{push_m}();")
            lines.append(f"            for (int i = 0; i < _n; i++) _inst.{pop_m}();")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"            for (int i = 0; i < _n; i++) _inst.{m_loop}();")
        lines.append("            _sw.Stop();")
        lines.append("            double _elapsed_ms = _sw.Elapsed.TotalMilliseconds;")
        lines.append(f"            int _ret = (int) _inst.{verify}();")
        lines.append("            " + _emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"            if (_ret != {expected}) {{")
        lines.append(f"                throw new System.Exception(\"FAIL: expected ret={expected}, got \" + _ret);")
        lines.append(f"            }}")
        lines.append(f"            {spec.println_pass.replace('nested-frame', 'perf')}")
        lines.append("        }")
        lines.append("    }")
        lines.append("}")

    elif lang == "c":
        lines.append("#include <stdio.h>")
        lines.append("#include <stdlib.h>")
        lines.append("#include <time.h>")
        lines.append("int main(void) {")
        lines.append(f"    {sys_name}* _inst = {sys_name}_new();")
        lines.append(f"    int _n = {n};")
        lines.append("    struct timespec _start, _end;")
        lines.append("    clock_gettime(CLOCK_MONOTONIC, &_start);")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"    for (int i = 0; i < _n; i++) {sys_name}_{push_m}(_inst);")
            lines.append(f"    for (int i = 0; i < _n; i++) {sys_name}_{pop_m}(_inst);")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"    for (int i = 0; i < _n; i++) {sys_name}_{m_loop}(_inst);")
        lines.append("    clock_gettime(CLOCK_MONOTONIC, &_end);")
        lines.append("    double _elapsed_ms = (_end.tv_sec - _start.tv_sec) * 1000.0 + (_end.tv_nsec - _start.tv_nsec) / 1e6;")
        lines.append(f"    int _ret = (int)(intptr_t){sys_name}_{verify}(_inst);")
        lines.append("    " + _emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        printf(\"FAIL: expected ret={expected}, got %d\\n\", _ret);")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perf')}")
        lines.append("    return 0;")
        lines.append("}")

    elif lang == "cpp":
        lines.append("#include <iostream>")
        lines.append("#include <chrono>")
        lines.append("int main() {")
        lines.append(f"    {sys_name} _inst;")
        lines.append(f"    int _n = {n};")
        lines.append("    auto _start = std::chrono::high_resolution_clock::now();")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"    for (int i = 0; i < _n; i++) _inst.{push_m}();")
            lines.append(f"    for (int i = 0; i < _n; i++) _inst.{pop_m}();")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"    for (int i = 0; i < _n; i++) _inst.{m_loop}();")
        lines.append("    auto _end = std::chrono::high_resolution_clock::now();")
        lines.append("    double _elapsed_ms = std::chrono::duration<double, std::milli>(_end - _start).count();")
        lines.append(f"    int _ret = std::any_cast<int>(_inst.{verify}());")
        lines.append("    " + _emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"    if (_ret != {expected}) {{")
        lines.append(f"        std::cerr << \"FAIL: expected ret={expected}, got \" << _ret << std::endl;")
        lines.append(f"        return 1;")
        lines.append(f"    }}")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perf')}")
        lines.append("    return 0;")
        lines.append("}")

    elif lang == "gdscript":
        lines.insert(2, "extends SceneTree")
        lines.insert(3, "")
        lines.append(spec.fail_exit_def)
        lines.append("func _init():")
        lines.append(f"    var _inst = {sys_name}.new()")
        lines.append(f"    var _n = {n}")
        lines.append("    var _start = Time.get_ticks_usec()")
        if is_p3:
            push_m = method_name(lang, "push_then")
            pop_m = method_name(lang, "go_back")
            lines.append(f"    for i in range(_n): _inst.{push_m}()")
            lines.append(f"    for i in range(_n): _inst.{pop_m}()")
        else:
            m_loop = method_name(lang, loop_m)
            lines.append(f"    for i in range(_n): _inst.{m_loop}()")
        lines.append("    var _elapsed_ms = (Time.get_ticks_usec() - _start) / 1000.0")
        lines.append(f"    var _ret = _inst.{verify}()")
        lines.append("    " + _emit_perf_line(lang, perf_str, "_n", "_elapsed_ms", "_ret"))
        lines.append(f"    if _ret != {expected}:")
        lines.append(f"        _fail(\"expected ret={expected}, got \" + str(_ret))")
        lines.append(f"    {spec.println_pass.replace('nested-frame', 'perf')}")
        lines.append("    quit()")

    elif lang == "erlang":
        # Erlang: runner generates the escript with the loop from
        # FUZZ_LOOP_* metadata. No driver in the source.
        pass

    return "\n".join(lines) + "\n"


def main():
    out_dir = Path(__file__).parent / "cases_perf"
    out_dir.mkdir(parents=True, exist_ok=True)

    index_lines = ["lang\tcase_id\tequiv_class\tsmoke\texpected\n"]

    cases_per_lang = {lang: 0 for lang in LANGS}
    smoke_per_lang = {lang: 0 for lang in LANGS}

    for cid, equiv, expected, pattern, tier_name, n, is_smoke in enumerate_cases():
        for lang in LANGS:
            spec = LANGS[lang]
            ext = spec.ext
            text = gen_case(lang, cid, equiv, expected, pattern, tier_name, n, is_smoke)
            (out_dir / f"{cid}.{ext}").write_text(text)
            cases_per_lang[lang] += 1
            if is_smoke:
                smoke_per_lang[lang] += 1
            index_lines.append(
                f"{lang}\t{cid}\t{equiv}\t{'yes' if is_smoke else 'no'}\t{expected}\n"
            )

    (out_dir / "_index.tsv").write_text("".join(index_lines))
    print(f"Generated cases in {out_dir}/")
    for lang in LANGS:
        print(f"  {lang}: {cases_per_lang[lang]} cases, {smoke_per_lang[lang]} smoke")


if __name__ == "__main__":
    main()
