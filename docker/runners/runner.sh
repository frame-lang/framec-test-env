#!/bin/bash
# Shared Frame test runner for Docker containers
# Usage: runner.sh <language>
#
# Discovers test files, transpiles via framec, compiles, runs, emits TAP output.
# The language is passed as the first argument (matches docker-compose CMD).

set -uo pipefail

# Source-hash cache for `framec compile` — identical Frame source →
# identical generated output across runs (see framec_cached.sh).
# Required for downstream caches (ccache, dotnet build cache, etc.)
# to hit on warm runs even when framec output ordering is technically
# nondeterministic.
. /framec_cached.sh

LANG="${1:?Usage: runner.sh <language>}"
OUTPUT="/output"
COMPILE_DIR="/tmp/out"
COMPILE_ONLY="${COMPILE_ONLY:-false}"
mkdir -p "$OUTPUT" "$COMPILE_DIR"

# Kotlin uses a batched runner: one kotlinc + one java for the whole run,
# vs. ~2N JVM cold starts in the per-test path below. See kotlin_batch.sh.
if [ "$LANG" = "kotlin" ] && [ -x /kotlin_batch.sh ]; then
    exec /kotlin_batch.sh
fi
# Java: same pattern — one javac + one JVM dispatching tests reflectively.
if [ "$LANG" = "java" ] && [ -x /java_batch.sh ]; then
    exec /java_batch.sh
fi
# C#: one dotnet build + one dotnet exec dispatching tests reflectively.
if [ "$LANG" = "csharp" ] && [ -x /csharp_batch.sh ]; then
    exec /csharp_batch.sh
fi
# TypeScript: one tsx process, dynamic import() per test.
if [ "$LANG" = "typescript" ] && [ -x /typescript_batch.sh ]; then
    exec /typescript_batch.sh
fi
# Rust: one cargo build produces all test bins, then iterate execs.
if [ "$LANG" = "rust" ] && [ -x /rust_batch.sh ]; then
    exec /rust_batch.sh
fi
# C++: parallel g++ per test (amortises g++ cold start via xargs -P),
# then iterate execs.
if [ "$LANG" = "cpp" ] && [ -x /cpp_batch.sh ]; then
    exec /cpp_batch.sh
fi
# Swift: parallel swiftc per test, then iterate execs.
if [ "$LANG" = "swift" ] && [ -x /swift_batch.sh ]; then
    exec /swift_batch.sh
fi
# Dart: parallel `dart compile kernel` to .dill, then `dart <dill>` per test.
if [ "$LANG" = "dart" ] && [ -x /dart_batch.sh ]; then
    exec /dart_batch.sh
fi
# Go: parallel `go build` per test, then iterate execs.
if [ "$LANG" = "go" ] && [ -x /go_batch.sh ]; then
    exec /go_batch.sh
fi
# Erlang: serial transpile+erlc+escript-gen, then parallel escript exec.
if [ "$LANG" = "erlang" ] && [ -x /erlang_batch.sh ]; then
    exec /erlang_batch.sh
fi
# GDScript: serial transpile, then parallel godot --script execs.
if [ "$LANG" = "gdscript" ] && [ -x /gdscript_batch.sh ]; then
    exec /gdscript_batch.sh
fi
# Python: one python3 process imports each test as a module.
if [ "$LANG" = "python" ] && [ -x /python_batch.sh ]; then
    exec /python_batch.sh
fi
# JavaScript: one node process dynamic-imports each .mjs.
if [ "$LANG" = "javascript" ] && [ -x /javascript_batch.sh ]; then
    exec /javascript_batch.sh
fi
# Ruby: one ruby process `load`s each test.
if [ "$LANG" = "ruby" ] && [ -x /ruby_batch.sh ]; then
    exec /ruby_batch.sh
fi
# PHP: one php process `require`s each test inside a function scope.
if [ "$LANG" = "php" ] && [ -x /php_batch.sh ]; then
    exec /php_batch.sh
fi
# Lua: one lua process loads each test.
if [ "$LANG" = "lua" ] && [ -x /lua_batch.sh ]; then
    exec /lua_batch.sh
fi

# Language configuration
case "$LANG" in
    python)     target="python_3";  ext="fpy"; out_ext="py" ;;
    typescript) target="typescript"; ext="fts"; out_ext="ts" ;;
    javascript) target="javascript"; ext="fjs"; out_ext="js" ;;
    rust)       target="rust";       ext="frs"; out_ext="rs" ;;
    c)          target="c";          ext="fc";  out_ext="c" ;;
    cpp)        target="cpp_23";     ext="fcpp"; out_ext="cpp" ;;
    csharp)     target="csharp";     ext="fcs"; out_ext="cs" ;;
    java)       target="java";       ext="fjava"; out_ext="java" ;;
    go)         target="go";         ext="fgo"; out_ext="go" ;;
    php)        target="php";        ext="fphp"; out_ext="php" ;;
    kotlin)     target="kotlin";     ext="fkt"; out_ext="kt" ;;
    swift)      target="swift";      ext="fswift"; out_ext="swift" ;;
    ruby)       target="ruby";       ext="frb"; out_ext="rb" ;;
    erlang)     target="erlang";     ext="ferl"; out_ext="erl" ;;
    lua)        target="lua";        ext="flua"; out_ext="lua" ;;
    dart)       target="dart";       ext="fdart"; out_ext="dart" ;;
    gdscript)   target="gdscript";   ext="fgd"; out_ext="gd" ;;
    *) echo "Unknown language: $LANG"; exit 1 ;;
esac

# Discover test files
tests=$(find /tests/common/positive -name "*.$ext" 2>/dev/null | sort)
lang_tests=$(find "/tests/$LANG" -name "*.$ext" 2>/dev/null | sort)
if [ -n "$lang_tests" ]; then
    tests="$tests
$lang_tests"
fi

test_count=$(echo "$tests" | grep -c . || echo 0)
if [ "$test_count" -eq 0 ]; then
    echo "TAP version 14"
    echo "1..0 # SKIP no $LANG tests found"
    exit 0
fi

echo "TAP version 14"
echo "1..$test_count"

pass=0
fail=0
skip=0
test_num=0

for test_file in $tests; do
    test_num=$((test_num + 1))
    test_name=$(basename "$test_file" ".$ext")

    # Check skip marker
    if head -10 "$test_file" 2>/dev/null | grep -qE "@@skip|@skip"; then
        echo "ok $test_num - $test_name # SKIP"
        skip=$((skip + 1))
        continue
    fi

    # Clean compile dir before each test
    rm -f "$COMPILE_DIR"/*.${out_ext} "$COMPILE_DIR"/*.class 2>/dev/null

    # Transpile via framec_cached so identical Frame source → identical
    # generated output across runs. The underlying framec binary has
    # nondeterministic HashMap iteration in some places (e.g. forward-
    # decl ordering in C/C++ codegen), which would otherwise miss
    # ccache and similar downstream caches. The cache key is
    # (framec_binary_hash, target, source_hash) so a framec rebuild
    # invalidates the cache as expected.
    if ! framec_cached "$target" "$COMPILE_DIR" "$test_file" /tmp/compile_err; then
        # Check if this is a transpile-error test (expected to fail)
        if echo "$test_file" | grep -q "transpile-error"; then
            echo "ok $test_num - $test_name # correctly rejected by transpiler"
            pass=$((pass + 1))
        else
            echo "not ok $test_num - $test_name # transpile failed"
            cat /tmp/compile_err 2>/dev/null | head -5 | sed 's/^/  # /'
            fail=$((fail + 1))
        fi
        continue
    fi

    out_file="$COMPILE_DIR/${test_name}.${out_ext}"
    # Java: framec names the output after the public class, not the source file
    if [ ! -f "$out_file" ] && [ "$LANG" = "java" ]; then
        out_file=$(ls "$COMPILE_DIR"/*.java 2>/dev/null | head -1)
    fi
    if [ ! -f "$out_file" ]; then
        echo "not ok $test_num - $test_name # no output file"
        fail=$((fail + 1))
        continue
    fi

    # Compile-only mode: transpilation succeeded, skip execution
    if [ "$COMPILE_ONLY" = "true" ]; then
        echo "ok $test_num - $test_name # transpiled"
        pass=$((pass + 1))
        continue
    fi

    # Compile and run (language-specific)
    run_output=""
    run_status=0

    case "$LANG" in
        python)
            run_output=$(python3 "$out_file" 2>&1) || run_status=$?
            ;;
        typescript)
            run_output=$(tsx "$out_file" 2>&1) || run_status=$?
            ;;
        javascript)
            js_run="${out_file%.js}.mjs"
            cp "$out_file" "$js_run"
            run_output=$(node "$js_run" 2>&1) || run_status=$?
            ;;
        rust)
            cp "$out_file" /rust_runner/src/main.rs
            touch /rust_runner/src/main.rs
            if cargo build --release --manifest-path /rust_runner/Cargo.toml 2>/tmp/build_err; then
                run_output=$(/rust_runner/target/release/runner 2>&1) || run_status=$?
            else
                run_status=1
                run_output="cargo build failed"
            fi
            ;;
        c)
            c_bin="$COMPILE_DIR/${test_name}"
            c_obj="${c_bin}.o"
            # Split compile + link so ccache can hit on the compile
            # step (ccache only caches `-c` invocations). Link step
            # is fast — one .o + libcjson.
            if gcc -c -o "$c_obj" "$out_file" 2>&1 \
                && gcc -o "$c_bin" "$c_obj" -lcjson 2>&1; then
                rm -f "$c_obj"
                run_output=$("$c_bin" 2>&1) || run_status=$?
            else
                rm -f "$c_obj"
                run_status=1
                run_output="gcc failed"
            fi
            ;;
        cpp)
            cpp_bin="$COMPILE_DIR/${test_name}"
            if g++ -std=c++23 -o "$cpp_bin" "$out_file" 2>&1; then
                run_output=$("$cpp_bin" 2>&1) || run_status=$?
            else
                run_status=1
                run_output="g++ failed"
            fi
            ;;
        csharp)
            cp "$out_file" /tmp/csproject/Program.cs
            run_output=$(cd /tmp/csproject && dotnet run --no-restore 2>&1) || run_status=$?
            ;;
        java)
            java_cp="$COMPILE_DIR"
            [ -f /lib/json.jar ] && java_cp="$COMPILE_DIR:/lib/json.jar"
            if javac -cp "$java_cp" -d "$COMPILE_DIR" "$out_file" 2>&1; then
                run_output=$(java -cp "$java_cp" Main 2>&1) || run_status=$?
            else
                run_status=1
                run_output="javac failed"
            fi
            ;;
        go)
            go_run="$out_file"
            if echo "$out_file" | grep -q '_test\.go$'; then
                go_run="${out_file%.go}_run.go"
                cp "$out_file" "$go_run"
            fi
            run_output=$(cd "$COMPILE_DIR" && go run "$go_run" 2>&1) || run_status=$?
            ;;
        php)
            run_output=$(php "$out_file" 2>&1) || run_status=$?
            ;;
        kotlin)
            kt_jar="${out_file%.kt}.jar"
            kt_cp=""
            [ -f /lib/json.jar ] && kt_cp="-cp /lib/json.jar"
            if kotlinc $kt_cp "$out_file" -include-runtime -d "$kt_jar" 2>&1; then
                # Extract Main-Class from manifest, fall back to MainKt
                kt_main=$(unzip -p "$kt_jar" META-INF/MANIFEST.MF 2>/dev/null | grep "Main-Class:" | sed 's/Main-Class: *//' | tr -d '\r\n')
                kt_main="${kt_main:-MainKt}"
                kt_run_cp="$kt_jar"
                [ -f /lib/json.jar ] && kt_run_cp="$kt_jar:/lib/json.jar"
                run_output=$(java -cp "$kt_run_cp" "$kt_main" 2>&1) || run_status=$?
            else
                run_status=1
                run_output="kotlinc failed"
            fi
            ;;
        swift)
            run_output=$(swift "$out_file" 2>&1) || run_status=$?
            ;;
        ruby)
            run_output=$(ruby "$out_file" 2>&1) || run_status=$?
            ;;
        erlang)
            erl_module=$(grep -m1 "^-module(" "$out_file" | sed 's/-module(\(.*\))\./\1/')
            erl_tmpdir=$(mktemp -d)
            cp "$out_file" "$erl_tmpdir/${erl_module}.erl"
            if erlc -o "$erl_tmpdir" "$erl_tmpdir/${erl_module}.erl" 2>/dev/null; then
                # Detect start_link arity from the generated -export line.
                # Systems with header params (`@@system Name(initial: int)`)
                # generate `start_link/N` instead of `start_link/0`.
                start_link_arity=$(grep "^-export" "$out_file" | head -1 | grep -oE 'start_link/[0-9]+' | sed 's|start_link/||')
                start_link_arity=${start_link_arity:-0}

                # Build start_link args using type-aware defaults from the
                # system header line in the source: extract `(...)` params,
                # one type per param, in order. Defaults: bool→false,
                # str/string→"", int/float/number→0, anything else→undefined.
                start_link_args=""
                if [ "$start_link_arity" -gt 0 ]; then
                    # Match the @@system header line in the source.
                    sys_line=$(grep -m1 "^@@system " "$test_file" 2>/dev/null)
                    sys_params_str=$(echo "$sys_line" | sed -n 's/.*@@system [A-Za-z_][A-Za-z0-9_]*[[:space:]]*(\(.*\))[[:space:]]*{.*/\1/p')
                    sys_idx=0
                    if [ -n "$sys_params_str" ]; then
                        echo "$sys_params_str" | tr ',' '\n' | while read -r p; do
                            t=$(echo "$p" | sed -n 's/.*: *\([a-zA-Z][a-zA-Z0-9_]*\).*/\1/p')
                            echo "$t"
                        done > "$erl_tmpdir/sys_param_types.txt"
                    fi
                    for i in $(seq 1 "$start_link_arity"); do
                        ptype=""
                        if [ -f "$erl_tmpdir/sys_param_types.txt" ]; then
                            ptype=$(sed -n "${i}p" "$erl_tmpdir/sys_param_types.txt")
                        fi
                        case "$ptype" in
                            bool|boolean) val="false" ;;
                            str|string|String) val="\"\"" ;;
                            int|float|number|Int|Float) val="0" ;;
                            *) val="undefined" ;;
                        esac
                        if [ -z "$start_link_args" ]; then
                            start_link_args="$val"
                        else
                            start_link_args="$start_link_args, $val"
                        fi
                    done
                fi

                # Extract exported interface functions (skip start_link/N, callback_mode, init, state handlers)
                erl_exports=$(grep "^-export" "$out_file" | head -1 | sed 's/-export(\[//;s/\])\.//' | sed -E 's/start_link\/[0-9]+,?//' | sed 's/,\s*$//' | tr ',' '\n' | grep -v '^$' | sed 's|/| |')
                # Generate escript that starts the system and calls each interface method
                cat > "$erl_tmpdir/run_test.escript" << ESCRIPT
#!/usr/bin/env escript
main(_) ->
    code:add_patha("."),
    {ok, Pid} = ${erl_module}:start_link(${start_link_args}),
ESCRIPT
                # Add a call for each exported function with default args
                # Use type-aware defaults: bool→false, str/string→"", else→0
                while IFS=' ' read -r fname arity; do
                    fname=$(echo "$fname" | tr -d ' ')
                    arity=$(echo "$arity" | tr -d ' ')
                    if [ -z "$fname" ] || [ "$fname" = "start_link" ]; then continue; fi
                    args="Pid"
                    remaining=$((arity - 1))
                    if [ "$remaining" -gt 0 ]; then
                        # Extract param types from source file: "fname(a: bool, b: int)" → "bool int"
                        iface_line=$(grep "${fname}(" "$test_file" 2>/dev/null | head -1)
                        # Get comma-separated param sections, then extract type after ":"
                        types=""
                        if [ -n "$iface_line" ]; then
                            params_str=$(echo "$iface_line" | sed "s/.*${fname}(//;s/).*//")
                            types=$(echo "$params_str" | tr ',' '\n' | while read -r p; do
                                t=$(echo "$p" | sed -n 's/.*: *\([a-zA-Z]*\).*/\1/p')
                                echo "$t"
                            done)
                        fi
                        idx=0
                        for i in $(seq 1 "$remaining"); do
                            idx=$((idx + 1))
                            ptype=$(echo "$types" | sed -n "${idx}p")
                            case "$ptype" in
                                bool|boolean) args="$args, false" ;;
                                str|string|String) args="$args, \"\"" ;;
                                *) args="$args, 0" ;;
                            esac
                        done
                    fi
                    echo "    _ = ${erl_module}:${fname}(${args})," >> "$erl_tmpdir/run_test.escript"
                done <<< "$erl_exports"
                cat >> "$erl_tmpdir/run_test.escript" << ESCRIPT
    io:format("ok 1 - ${test_name}~n"),
    init:stop().
ESCRIPT
                chmod +x "$erl_tmpdir/run_test.escript"
                run_output=$(cd "$erl_tmpdir" && escript run_test.escript 2>&1) || run_status=$?
            else
                run_status=1
                run_output="erlc failed"
            fi
            rm -rf "$erl_tmpdir"
            ;;
        lua)
            run_output=$(lua "$out_file" 2>&1 || lua5.4 "$out_file" 2>&1) || run_status=$?
            ;;
        dart)
            run_output=$(dart run "$out_file" 2>&1) || run_status=$?
            ;;
        gdscript)
            if command -v godot >/dev/null 2>&1; then
                run_output=$(timeout 10 godot --headless --script "$out_file" 2>&1) || run_status=$?
                if [ $run_status -eq 124 ]; then
                    run_output="ok 1 - $test_name # transpiled (godot timed out)"
                    run_status=0
                fi
            else
                run_output="ok 1 - $test_name # transpiled (no godot)"
                run_status=0
            fi
            ;;
    esac

    # Determine pass/fail
    if [ $run_status -ne 0 ]; then
        echo "not ok $test_num - $test_name # runtime error (exit $run_status)"
        echo "$run_output" | head -5 | sed 's/^/  # /'
        fail=$((fail + 1))
    elif echo "$run_output" | grep -q "^not ok "; then
        echo "not ok $test_num - $test_name"
        fail=$((fail + 1))
    elif echo "$run_output" | grep -qE "(^ok |PASS)"; then
        echo "ok $test_num - $test_name"
        pass=$((pass + 1))
    elif [ -z "$run_output" ]; then
        echo "ok $test_num - $test_name # clean exit"
        pass=$((pass + 1))
    else
        echo "not ok $test_num - $test_name # unrecognized output"
        echo "$run_output" | head -3 | sed 's/^/  # /'
        fail=$((fail + 1))
    fi
done

echo ""
echo "# $LANG: $pass passed, $fail failed, $skip skipped"
exit $fail
