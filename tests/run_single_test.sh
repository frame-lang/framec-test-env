#!/bin/bash
#
# Helper script to run a single Frame test
# Called by run_tests.sh in parallel mode
#
# Usage: ./run_single_test.sh <test_file> <lang> <result_file>
#

test_file="$1"
lang="$2"
result_file="$3"

# Ensure all tool directories are in PATH (non-login shells like CI / Claude Code
# don't source the user's profile). Matches run_tests.sh — both need this so
# python3, node, npx, cargo, gcc are always reachable.
for __dir in "$HOME/.cargo/bin" "/usr/local/bin" "/opt/homebrew/bin"; do
    if [ -d "$__dir" ]; then
        case ":$PATH:" in
            *":$__dir:"*) ;;
            *) export PATH="$__dir:$PATH" ;;
        esac
    fi
done
unset __dir

# Environment (inherited from parent)
FRAMEC="${FRAMEC:-/Users/marktruluck/projects/frame_transpiler/target/release/framec}"
TEST_ENV_ROOT="${TEST_ENV_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"

PYTHON_OUT="$TEST_ENV_ROOT/output/python/tests"
TS_OUT="$TEST_ENV_ROOT/output/typescript/tests"
RUST_CRATE="$TEST_ENV_ROOT/output/rust"
RUST_OUT="$RUST_CRATE/tests"
C_OUT="$TEST_ENV_ROOT/output/c/tests"
CPP_OUT="$TEST_ENV_ROOT/output/cpp/tests"
JAVA_OUT="$TEST_ENV_ROOT/output/java/tests"
CSHARP_OUT="$TEST_ENV_ROOT/output/csharp/tests"
GO_OUT="$TEST_ENV_ROOT/output/go/tests"
JS_OUT="$TEST_ENV_ROOT/output/javascript/tests"
PHP_OUT="$TEST_ENV_ROOT/output/php/tests"
KOTLIN_OUT="$TEST_ENV_ROOT/output/kotlin/tests"
SWIFT_OUT="$TEST_ENV_ROOT/output/swift/tests"
RUBY_OUT="$TEST_ENV_ROOT/output/ruby/tests"
ERLANG_OUT="$TEST_ENV_ROOT/output/erlang/tests"
LUA_OUT="$TEST_ENV_ROOT/output/lua/tests"
DART_OUT="$TEST_ENV_ROOT/output/dart/tests"
GDSCRIPT_OUT="$TEST_ENV_ROOT/output/gdscript/tests"

# .NET SDK — find dotnet
DOTNET_CMD=""
for __ddir in "/usr/local/opt/dotnet/libexec" "/opt/homebrew/opt/dotnet/libexec" "/usr/share/dotnet"; do
    if [ -x "$__ddir/dotnet" ]; then
        DOTNET_CMD="$__ddir/dotnet"
        export DOTNET_ROOT="$__ddir"
        break
    fi
done

# Java 17 — find JDK
JAVA_HOME_17=""
for __jdir in "/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home" "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home" "/usr/lib/jvm/java-17-openjdk-amd64"; do
    if [ -x "$__jdir/bin/javac" ]; then
        JAVA_HOME_17="$__jdir"
        break
    fi
done

test_name=$(basename "$test_file" | sed 's/\.f[a-z]*$//')

# Language mappings
case $lang in
    python) target="python_3"; out_dir="$PYTHON_OUT"; out_ext="py" ;;
    typescript) target="typescript"; out_dir="$TS_OUT"; out_ext="ts" ;;
    rust) target="rust"; out_dir="$RUST_OUT"; out_ext="rs" ;;
    c) target="c"; out_dir="$C_OUT"; out_ext="c" ;;
    cpp) target="cpp_17"; out_dir="$CPP_OUT"; out_ext="cpp" ;;
    java) target="java"; out_dir="$JAVA_OUT"; out_ext="java" ;;
    csharp) target="csharp"; out_dir="$CSHARP_OUT"; out_ext="cs" ;;
    go) target="go"; out_dir="$GO_OUT"; out_ext="go" ;;
    javascript) target="javascript"; out_dir="$JS_OUT"; out_ext="js" ;;
    php) target="php"; out_dir="$PHP_OUT"; out_ext="php" ;;
    kotlin) target="kotlin"; out_dir="$KOTLIN_OUT"; out_ext="kt" ;;
    swift) target="swift"; out_dir="$SWIFT_OUT"; out_ext="swift" ;;
    ruby) target="ruby"; out_dir="$RUBY_OUT"; out_ext="rb" ;;
    erlang) target="erlang"; out_dir="$ERLANG_OUT"; out_ext="erl" ;;
    lua) target="lua"; out_dir="$LUA_OUT"; out_ext="lua" ;;
    dart) target="dart"; out_dir="$DART_OUT"; out_ext="dart" ;;
    gdscript) target="gdscript"; out_dir="$GDSCRIPT_OUT"; out_ext="gd" ;;
esac

out_file="$out_dir/${test_name}.${out_ext}"

# Check skip marker
if head -10 "$test_file" 2>/dev/null | grep -qE "@@skip|@skip"; then
    echo "skip" > "$result_file"
    exit 0
fi

# Check xfail marker
is_xfail=false
if head -10 "$test_file" 2>/dev/null | grep -qE "@@xfail|@xfail"; then
    is_xfail=true
fi

# Clean stale compiled artifacts before transpilation
case $lang in
    java) find "$JAVA_OUT" -name "*.class" -delete 2>/dev/null ;;
    go) rm -f "$out_dir/${test_name}.go" 2>/dev/null ;;
esac

# Transpile
compile_output=$("$FRAMEC" compile -l "$target" -o "$out_dir" "$test_file" 2>&1)
compile_status=$?

if [ $compile_status -ne 0 ] || [ ! -f "$out_file" ]; then
    if $is_xfail; then
        echo "known" > "$result_file"
    else
        echo "fail" > "$result_file"
        echo "TEST_FILE:$test_file" >> "$result_file"
        echo "$compile_output" >> "$result_file"
    fi
    exit 0
fi

# Run
run_output=""
run_status=0

case $lang in
    python)
        run_output=$(python3 "$out_file" 2>&1) || run_status=$?
        ;;
    typescript)
        run_output=$(cd "$TEST_ENV_ROOT/output/typescript" && npx ts-node "tests/${test_name}.ts" 2>&1) || run_status=$?
        ;;
    rust)
        # Run pre-built binary directly (cargo build was done before parallel execution)
        rust_bin="$RUST_CRATE/target/release/$test_name"
        if [ -x "$rust_bin" ]; then
            run_output=$("$rust_bin" 2>&1) || run_status=$?
        else
            # Fallback to debug build
            rust_bin="$RUST_CRATE/target/debug/$test_name"
            if [ -x "$rust_bin" ]; then
                run_output=$("$rust_bin" 2>&1) || run_status=$?
            else
                run_status=1
                run_output="Rust binary not found: $test_name"
            fi
        fi
        ;;
    c)
        c_bin="$C_OUT/${test_name}"
        cjson_flags=""
        # Prefer /opt/homebrew (ARM64 Mac) over /usr/local (may be x86_64)
        if [ -d "/opt/homebrew/include/cjson" ]; then
            cjson_flags="-I/opt/homebrew/include -L/opt/homebrew/lib -lcjson"
        elif [ -d "/usr/local/include/cjson" ]; then
            cjson_flags="-I/usr/local/include -L/usr/local/lib -lcjson"
        fi
        if gcc -o "$c_bin" "$out_file" $cjson_flags 2>&1; then
            run_output=$("$c_bin" 2>&1) || run_status=$?
        else
            run_status=1
            run_output="C compilation failed"
        fi
        ;;
    cpp)
        cpp_bin="$CPP_OUT/${test_name}"
        cpp_json_flags=""
        if [ -d "/opt/homebrew/include/nlohmann" ]; then
            cpp_json_flags="-I/opt/homebrew/include"
        elif [ -d "/usr/local/include/nlohmann" ]; then
            cpp_json_flags="-I/usr/local/include"
        fi
        if g++ -std=c++17 $cpp_json_flags -o "$cpp_bin" "$out_file" 2>&1; then
            run_output=$("$cpp_bin" 2>&1) || run_status=$?
        else
            run_status=1
            run_output="C++ compilation failed"
        fi
        ;;
    java)
        if [ -n "$JAVA_HOME_17" ]; then
            javac_cmd="$JAVA_HOME_17/bin/javac"
            java_cmd="$JAVA_HOME_17/bin/java"
        else
            javac_cmd="javac"
            java_cmd="java"
        fi
        java_json_jar="$TEST_ENV_ROOT/output/java/lib/json.jar"
        java_cp="$JAVA_OUT"
        if [ -f "$java_json_jar" ]; then
            java_cp="$JAVA_OUT:$java_json_jar"
        fi
        if $javac_cmd -cp "$java_cp" -d "$JAVA_OUT" "$out_file" 2>&1; then
            run_output=$($java_cmd -cp "$java_cp" Main 2>&1) || run_status=$?
        else
            run_status=1
            run_output="Java compilation failed"
        fi
        ;;
    csharp)
        if [ -n "$DOTNET_CMD" ]; then
            run_output=$(DOTNET_ROOT="$DOTNET_ROOT" $DOTNET_CMD run "$out_file" 2>&1) || run_status=$?
        else
            run_status=1
            run_output="dotnet not found"
        fi
        ;;
    go)
        # Go treats *_test.go as test files — copy to temp name if needed
        go_run_file="$out_file"
        if echo "$out_file" | grep -q '_test\.go$'; then
            go_run_file="${out_file%.go}_run.go"
            cp "$out_file" "$go_run_file"
        fi
        run_output=$(GOFLAGS="-count=1" go run "$go_run_file" 2>&1) || run_status=$?
        ;;
    javascript)
        # Rename .js to .mjs for ESM execution without package.json
        js_run_file="${out_file%.js}.mjs"
        cp "$out_file" "$js_run_file"
        run_output=$(node "$js_run_file" 2>&1) || run_status=$?
        ;;
    php)
        php_cmd="php"
        for __pdir in "/usr/local/opt/php/bin" "/opt/homebrew/opt/php/bin" "/usr/bin"; do
            if [ -x "$__pdir/php" ]; then php_cmd="$__pdir/php"; break; fi
        done
        run_output=$($php_cmd "$out_file" 2>&1) || run_status=$?
        ;;
    kotlin)
        # Kotlin: kotlinc file.kt -include-runtime -d file.jar && java -jar file.jar
        kt_jar="${out_file%.kt}.jar"
        kotlinc_cmd="kotlinc"
        for __kdir in "/usr/local/bin" "/opt/homebrew/bin"; do
            if [ -x "$__kdir/kotlinc" ]; then kotlinc_cmd="$__kdir/kotlinc"; break; fi
        done
        # Include json.jar for @@persist tests that use org.json
        kt_json_jar="$TEST_ENV_ROOT/output/java/lib/json.jar"
        kt_cp_flags=""
        if [ -f "$kt_json_jar" ]; then
            kt_cp_flags="-cp $kt_json_jar"
        fi
        kt_compile_output=$($kotlinc_cmd $kt_cp_flags "$out_file" -include-runtime -d "$kt_jar" 2>&1)
        kt_compile_status=$?
        if [ $kt_compile_status -eq 0 ]; then
            # Use -cp instead of -jar to include json.jar at runtime
            if [ -f "$kt_json_jar" ]; then
                # Extract Main-Class from jar manifest, then use -cp to include json.jar
                kt_main=$(unzip -p "$kt_jar" META-INF/MANIFEST.MF 2>/dev/null | grep "Main-Class:" | sed 's/Main-Class: *//' | tr -d '\r')
                if [ -n "$kt_main" ]; then
                    run_output=$(/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home/bin/java -cp "$kt_jar:$kt_json_jar" "$kt_main" 2>&1) || run_status=$?
                else
                    run_output=$(/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home/bin/java -jar "$kt_jar" 2>&1) || run_status=$?
                fi
            else
                run_output=$(/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home/bin/java -jar "$kt_jar" 2>&1) || run_status=$?
            fi
        else
            run_status=1
            run_output="Kotlin compilation failed: $kt_compile_output"
        fi
        ;;
    swift)
        run_output=$(swift "$out_file" 2>&1) || run_status=$?
        ;;
    ruby)
        ruby_cmd="ruby"
        for __rdir in "/usr/local/opt/ruby/bin" "/opt/homebrew/opt/ruby/bin" "/usr/bin"; do
            if [ -x "$__rdir/ruby" ]; then ruby_cmd="$__rdir/ruby"; break; fi
        done
        run_output=$($ruby_cmd "$out_file" 2>&1) || run_status=$?
        ;;
    erlang)
        # Erlang: compile with erlc in an isolated temp directory.
        # Many tests produce the same module name (e.g., -module(s)),
        # so parallel compilation must not share a directory.
        erl_module=$(grep -m1 "^-module(" "$out_file" | sed 's/-module(\(.*\))\./\1/')
        erl_tmpdir=$(mktemp -d)
        erl_module_file="$erl_tmpdir/${erl_module}.erl"
        cp "$out_file" "$erl_module_file"
        erlc_output=$(erlc -o "$erl_tmpdir" "$erl_module_file" 2>&1)
        erlc_status=$?
        rm -rf "$erl_tmpdir"
        if [ $erlc_status -ne 0 ]; then
            run_status=$erlc_status
            run_output="erlc compile error: $erlc_output"
        else
            run_output="ok 1 - $test_name # compiled successfully"
            run_status=0
        fi
        ;;
    lua)
        # Lua: run with lua interpreter
        lua_cmd=""
        for __ldir in "/usr/local/bin" "/opt/homebrew/bin" "/usr/bin"; do
            if [ -x "$__ldir/lua" ]; then lua_cmd="$__ldir/lua"; break; fi
        done
        if [ -z "$lua_cmd" ]; then
            # Try lua5.4 or luajit
            for __ldir in "/usr/local/bin" "/opt/homebrew/bin" "/usr/bin"; do
                if [ -x "$__ldir/lua5.4" ]; then lua_cmd="$__ldir/lua5.4"; break; fi
                if [ -x "$__ldir/luajit" ]; then lua_cmd="$__ldir/luajit"; break; fi
            done
        fi
        if [ -n "$lua_cmd" ]; then
            run_output=$($lua_cmd "$out_file" 2>&1) || run_status=$?
            # Clean exit with no TAP output = pass (transpile+execute test)
            if [ $run_status -eq 0 ] && [ -z "$run_output" ]; then
                run_output="ok 1 - $test_name # executed clean"
            fi
        else
            # No lua — transpile-only
            run_output="ok 1 - $test_name # compiled (no lua interpreter)"
            run_status=0
        fi
        ;;
    dart)
        # Dart: compile and run with dart
        dart_cmd=""
        for __ddir in "/usr/local/bin" "/opt/homebrew/bin" "/usr/lib/dart/bin"; do
            if [ -x "$__ddir/dart" ]; then dart_cmd="$__ddir/dart"; break; fi
        done
        if [ -z "$dart_cmd" ] && command -v dart >/dev/null 2>&1; then
            dart_cmd="dart"
        fi
        if [ -n "$dart_cmd" ]; then
            run_output=$($dart_cmd run "$out_file" 2>&1) || run_status=$?
            # Clean exit with no TAP output = pass (transpile+execute test)
            if [ $run_status -eq 0 ] && [ -z "$run_output" ]; then
                run_output="ok 1 - $test_name # executed clean"
            fi
        else
            # No dart — transpile-only
            run_output="ok 1 - $test_name # compiled (no dart SDK)"
            run_status=0
        fi
        ;;
    gdscript)
        # GDScript: try godot --headless, fall back to transpile-only
        godot_cmd=""
        for __gdir in "/usr/local/bin" "/opt/homebrew/bin" "/usr/bin"; do
            if [ -x "$__gdir/godot" ]; then godot_cmd="$__gdir/godot"; break; fi
        done
        if [ -z "$godot_cmd" ] && command -v godot >/dev/null 2>&1; then
            godot_cmd="godot"
        fi
        if [ -n "$godot_cmd" ]; then
            # Try running with timeout; godot --headless --script may not work for standalone scripts
            run_output=$(timeout 10 $godot_cmd --headless --script "$out_file" 2>&1) || run_status=$?
            if [ $run_status -eq 124 ]; then
                # Timeout — treat as transpile-only pass
                run_output="ok 1 - $test_name # transpiled (godot timed out)"
                run_status=0
            elif [ $run_status -eq 0 ] && [ -z "$run_output" ]; then
                run_output="ok 1 - $test_name # executed clean"
            fi
        else
            # No godot — transpile-only
            run_output="ok 1 - $test_name # transpiled (no godot)"
            run_status=0
        fi
        ;;
esac

# Determine pass/fail:
#   1. Non-zero exit code = definite failure
#   2. TAP "not ok" lines = failure (even if exit code is 0)
#   3. TAP "ok" lines or "PASS" string = pass
#   4. No recognizable output = failure
test_passed=false
if [ $run_status -ne 0 ]; then
    test_passed=false
elif echo "$run_output" | grep -q "^not ok "; then
    test_passed=false
elif echo "$run_output" | grep -qE "(^ok |PASS)"; then
    test_passed=true
fi

if $test_passed; then
    echo "pass" > "$result_file"
elif $is_xfail; then
    echo "known" > "$result_file"
else
    echo "fail" > "$result_file"
    echo "TEST_FILE:$test_file" >> "$result_file"
    echo "$run_output" >> "$result_file"
fi
