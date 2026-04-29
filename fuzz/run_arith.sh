#!/usr/bin/env bash
# Phase 15 — runs the state-arg propagation fuzz cases generated
# by `gen_arith.py`. Sibling of run_nested.sh; same per-language
# transpile + compile + run pipeline. Adds:
#   - `--tier=smoke|core|full` (default `full`).
#   - `--lang=<name>` to scope to one language; default all 17.
# Smoke filter greps each case file for `FUZZ_SMOKE: yes`. Core tier
# delegates to run_nested.sh (the curated regression set
# p7/p8/p9/p11/p14).

set -o pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
FRAMEC=${FRAMEC:-/Users/marktruluck/projects/framepiler/target/release/framec}
CASES_DIR=$SCRIPT_DIR/cases_arith
OUT_DIR=$SCRIPT_DIR/out_arith
LOG_DIR=$SCRIPT_DIR/logs_arith
mkdir -p "$OUT_DIR" "$LOG_DIR"

TIER="full"
EXPLICIT_LANGS=""
while [ $# -gt 0 ]; do
    case "$1" in
        --tier=*) TIER="${1#--tier=}" ;;
        --tier) shift; TIER="$1" ;;
        --lang=*) EXPLICIT_LANGS="${EXPLICIT_LANGS} ${1#--lang=}" ;;
        --lang) shift; EXPLICIT_LANGS="${EXPLICIT_LANGS} $1" ;;
        --help|-h)
            echo "Usage: $0 [--tier=smoke|core|full] [--lang=<name>] [<lang1> <lang2> ...]"
            exit 0
            ;;
        *) EXPLICIT_LANGS="${EXPLICIT_LANGS} $1" ;;
    esac
    shift || true
done

LANGS=${EXPLICIT_LANGS:-"python_3 javascript typescript ruby lua php dart rust go swift java kotlin csharp c cpp gdscript erlang"}

# Core tier delegates to run_nested.sh — its remaining 4 curated
# patterns (p7, p8, p9, p11) ARE the core regression set.
if [ "$TIER" = "core" ]; then
    exec "$SCRIPT_DIR/run_nested.sh" $LANGS
fi

if [ "$TIER" != "smoke" ] && [ "$TIER" != "full" ]; then
    echo "unknown --tier=$TIER (expected smoke|core|full)" >&2
    exit 2
fi

# Per-lang summary files so concurrent --lang=X / --lang=Y
# invocations don't clobber each other. Each run truncates only
# the summary files for its own LANGS scope.
PER_LANG_LOG_DIR=$LOG_DIR/per_lang
mkdir -p "$PER_LANG_LOG_DIR"
for ln in $LANGS; do
    f="$PER_LANG_LOG_DIR/summary_$ln.tsv"
    : > "$f"
    printf "lang\tcase\tstage\tresult\terror\n" >> "$f"
done
# Aggregate `summary.tsv` is REBUILT at end-of-script from the
# per-lang files; intra-run reads should target the per-lang file.
# `$summary` is set per-iteration in the lang loop below.

lang_to_ext() {
    case "$1" in
        python_3)   echo fpy ;;
        javascript) echo fjs ;;
        typescript) echo fts ;;
        ruby)       echo frb ;;
        lua)        echo flua ;;
        php)        echo fphp ;;
        dart)       echo fdart ;;
        rust)       echo frs ;;
        go)         echo fgo ;;
        swift)      echo fswift ;;
        java)       echo fjava ;;
        kotlin)     echo fkt ;;
        csharp)     echo fcs ;;
        c)          echo fc ;;
        cpp)        echo fcpp ;;
        gdscript)   echo fgd ;;
        erlang)     echo ferl ;;
        *)          echo unknown ;;
    esac
}

# Filter: emit case file paths matching the active tier.
# Reads `_index.tsv` (lang \t case_id \t equiv_class \t smoke \t expected)
# emitted by gen_perm.py. In smoke mode, we only run rows tagged
# `smoke=yes`. Cache the smoke set in an associative array keyed by
# `<lang>:<case_id>`.
INDEX_FILE="$CASES_DIR/_index.tsv"
# Build a smoke key list (lang:case_id, one per line). The runner's
# smoke filter scans this list. Using a flat file rather than a bash
# associative array keeps the script portable across older bash
# versions on macOS (3.x) where `declare -A` doesn't always behave
# the same as Linux bash 4+.
SMOKE_KEYS=$LOG_DIR/smoke_keys.txt
: > "$SMOKE_KEYS"
if [ -f "$INDEX_FILE" ]; then
    awk -F'\t' 'NR>1 && $4 == "yes" {print $1 ":" $2}' "$INDEX_FILE" > "$SMOKE_KEYS"
fi

should_run_case() {
    local lang=$1 case_file=$2
    if [ "$TIER" = "smoke" ]; then
        local cid
        cid=$(basename "$case_file" | sed 's/\.f[a-z]*$//')
        grep -qx "${lang}:${cid}" "$SMOKE_KEYS" || return 1
    fi
    return 0
}

run_one() {
    local lang=$1 case_file=$2
    local case_id
    case_id=$(basename "$case_file" | sed 's/\.f[a-z]*$//')
    local out="$OUT_DIR/$lang/$case_id"
    local errlog="$LOG_DIR/$lang-$case_id.err"

    # Kotlin batched fast path.
    if [ "$lang" = "kotlin" ] && [ -n "${KOTLIN_BATCH_JAR:-}" ]; then
        local main_class="nf_${case_id}.Driver"
        local result rc=0
        result=$(java -classpath "$KOTLIN_BATCH_JAR" "$main_class" 2>&1)
        rc=$?
        if [ $rc -eq 0 ] && echo "$result" | grep -q "^PASS"; then
            printf "%s\t%s\trun\tPASS\t\n" "$lang" "$case_id" >> "$summary"
            return 0
        fi
        local e
        e=$(echo "$result" | head -3 | tr '\n' '|' | head -c 220)
        printf "%s\t%s\trun\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
        return 1
    fi

    # C# batched fast path.
    if [ "$lang" = "csharp" ] && [ -n "${CSHARP_BATCH_OUT:-}" ]; then
        if grep -q "^DISP_${case_id}: OK" "$CSHARP_BATCH_OUT" 2>/dev/null; then
            printf "%s\t%s\trun\tPASS\t\n" "$lang" "$case_id" >> "$summary"
            return 0
        fi
        local line
        line=$(grep "^DISP_${case_id}:" "$CSHARP_BATCH_OUT" 2>/dev/null | head -1)
        printf "%s\t%s\trun\tFAIL\t%s\n" "$lang" "$case_id" "$line" >> "$summary"
        return 1
    fi

    # Java batched fast path. Each test source has `package nf_<id>;`
    # so a single javac invocation compiles all tests at once into
    # `JAVA_BATCH_CLASSES/nf_<id>/Driver.class`. Per-test execution
    # is `java -cp <classes> nf_<id>.Driver`.
    if [ "$lang" = "java" ] && [ -n "${JAVA_BATCH_CLASSES:-}" ]; then
        local main_class="nf_${case_id}.Driver"
        local result rc=0
        result=$(java -cp "$JAVA_BATCH_CLASSES" "$main_class" 2>&1)
        rc=$?
        if [ $rc -eq 0 ] && echo "$result" | grep -q "^PASS"; then
            printf "%s\t%s\trun\tPASS\t\n" "$lang" "$case_id" >> "$summary"
            return 0
        fi
        local e
        e=$(echo "$result" | head -3 | tr '\n' '|' | head -c 220)
        printf "%s\t%s\trun\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
        return 1
    fi

    rm -rf "$out" 2>/dev/null
    mkdir -p "$out"

    if ! "$FRAMEC" compile -l "$lang" -o "$out" "$case_file" > "$errlog" 2>&1; then
        local e
        e=$(head -3 "$errlog" | grep -v frame_runtime | tr '\n' '|' | head -c 220)
        printf "%s\t%s\ttranspile\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
        return 1
    fi

    local gen
    gen=$(ls "$out"/*.* 2>/dev/null | head -1)
    if [ -z "$gen" ]; then
        printf "%s\t%s\ttranspile\tFAIL\tno output\n" "$lang" "$case_id" >> "$summary"
        return 1
    fi

    local result rc=0
    case "$lang" in
        python_3)
            result=$(python3 "$gen" 2>&1); rc=$? ;;
        javascript)
            local mjs="${gen%.js}.mjs"
            cp "$gen" "$mjs"
            result=$(node "$mjs" 2>&1); rc=$? ;;
        typescript)
            result=$(tsx "$gen" 2>&1); rc=$? ;;
        ruby)
            result=$(ruby "$gen" 2>&1); rc=$? ;;
        lua)
            result=$(lua "$gen" 2>&1); rc=$? ;;
        php)
            result=$(php "$gen" 2>&1); rc=$? ;;
        dart)
            result=$(dart run "$gen" 2>&1); rc=$? ;;
        rust)
            local bin="$out/bin"
            if ! rustc -o "$bin" "$gen" 2>"$errlog"; then
                local e
                e=$(head -3 "$errlog" | tr '\n' '|' | head -c 220)
                printf "%s\t%s\tcompile\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
                return 1
            fi
            result=$("$bin" 2>&1); rc=$? ;;
        go)
            result=$(go run "$gen" 2>&1); rc=$? ;;
        swift)
            result=$(swift "$gen" 2>&1); rc=$? ;;
        java)
            # Per-case fallback path (used when batch_java didn't run
            # or failed to set JAVA_BATCH_CLASSES). Inject
            # `package nf_<id>;` at the top of the framec .java output
            # — same workaround as batch_java for the framec import-
            # before-prolog ordering issue.
            local target_java="${gen%.java}.java"
            local tmp="$target_java.tmp"
            { printf "package nf_%s;\n\n" "$case_id"; cat "$target_java"; } > "$tmp" && mv "$tmp" "$target_java"
            if ! (cd "$out" && javac "$target_java") 2>"$errlog"; then
                local e
                e=$(head -3 "$errlog" | tr '\n' '|' | head -c 220)
                printf "%s\t%s\tcompile\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
                return 1
            fi
            result=$(cd "$out" && java "nf_${case_id}.Driver" 2>&1); rc=$? ;;
        kotlin)
            local jar="$out/test.jar"
            if ! kotlinc "$gen" -include-runtime -d "$jar" 2>"$errlog"; then
                local e
                e=$(head -3 "$errlog" | tr '\n' '|' | head -c 220)
                printf "%s\t%s\tcompile\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
                return 1
            fi
            result=$(java -jar "$jar" 2>&1); rc=$? ;;
        csharp)
            local proj_dir="$out/proj"
            mkdir -p "$proj_dir"
            cp "$gen" "$proj_dir/Program.cs"
            cat > "$proj_dir/test.csproj" <<CSPROJ
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>disable</Nullable>
    <RootNamespace>PermFuzz</RootNamespace>
  </PropertyGroup>
</Project>
CSPROJ
            (cd "$proj_dir" && dotnet restore -v q >"$errlog" 2>&1) || true
            result=$(cd "$proj_dir" && dotnet run -v q 2>&1); rc=$? ;;
        c)
            local bin="$out/bin"
            if ! gcc -o "$bin" "$gen" 2>"$errlog"; then
                local e
                e=$(head -3 "$errlog" | tr '\n' '|' | head -c 220)
                printf "%s\t%s\tcompile\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
                return 1
            fi
            result=$("$bin" 2>&1); rc=$? ;;
        cpp)
            local bin="$out/bin"
            if ! g++ -std=c++17 -o "$bin" "$gen" 2>"$errlog"; then
                local e
                e=$(head -3 "$errlog" | tr '\n' '|' | head -c 220)
                printf "%s\t%s\tcompile\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
                return 1
            fi
            result=$("$bin" 2>&1); rc=$? ;;
        gdscript)
            result=$(godot --headless --script "$gen" --quit-after 1 2>&1); rc=$? ;;
        erlang)
            local expected_n
            expected_n=$(grep '^%% FUZZ_EXPECTED_N:' "$case_file" | awk '{print $3}')
            local drive_arg
            drive_arg=$(grep '^%% FUZZ_DRIVE_ARG:' "$case_file" | awk '{print $3}')
            local verify_method
            verify_method=$(grep '^%% FUZZ_VERIFY_METHOD:' "$case_file" | awk '{print $3}')
            local drive_returns
            drive_returns=$(grep '^%% FUZZ_DRIVE_RETURNS:' "$case_file" | awk '{print $3}')
            local mod
            mod=$(grep -m1 '^-module(' "$gen" | sed 's/-module(\(.*\))\./\1/')
            if [ -z "$mod" ]; then
                printf "%s\t%s\tcompile\tFAIL\tno -module\n" "$lang" "$case_id" >> "$summary"
                return 1
            fi
            local target_erl="$out/${mod}.erl"
            if [ "$gen" != "$target_erl" ]; then
                cp "$gen" "$target_erl"
            fi
            if ! (cd "$out" && erlc "$target_erl") 2>"$errlog"; then
                local e
                e=$(head -3 "$errlog" | tr '\n' '|' | head -c 220)
                printf "%s\t%s\tcompile\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
                return 1
            fi
            local escript="$out/drive.escript"
            # Build the drive + verify sequence based on the
            # in-source flags. For v2 dom/sv LHS, drive() is void
            # (returns gen_statem's `ok` reply) and we call the
            # verify method afterwards. For ret LHS, drive() itself
            # returns the value and there's no verify call.
            # Phase 15 drive() takes no args; drive_arg metadata
            # empty. Empty → drive/1; non-empty → drive/2.
            # P8 (FUZZ_PRE_DRIVE) needs drive() called first then
            # drive2() called for verify — same drive/1 form.
            local drive_call
            if [ -z "$drive_arg" ]; then
                drive_call="${mod}:drive(Pid)"
            else
                drive_call="${mod}:drive(Pid, ${drive_arg})"
            fi
            local pre_drive
            pre_drive=$(grep '^%% FUZZ_PRE_DRIVE:' "$case_file" | awk '{print $3}')
            local body
            if [ -n "$pre_drive" ]; then
                # P8-style: pre_drive transitions, verify_method
                # reads the persisted state arg.
                body="    _ = ${mod}:${pre_drive}(Pid),
    Ret = ${mod}:${verify_method}(Pid),"
            elif [ "${drive_returns:-yes}" = "yes" ]; then
                body="    Ret = ${drive_call},"
            else
                body="    _ = ${drive_call},
    Ret = ${mod}:${verify_method:-get_n}(Pid),"
            fi
            cat > "$escript" <<ESCRIPT
#!/usr/bin/env escript
main(_) ->
    code:add_patha("$out"),
    {ok, Pid} = ${mod}:start_link(),
${body}
    Expected = ${expected_n},
    case Ret of
        Expected -> io:format("PASS: arith~n");
        Other ->
            io:format("FAIL: expected ret=~p, got ~p~n", [Expected, Other]),
            halt(1)
    end.
ESCRIPT
            chmod +x "$escript"
            result=$(escript "$escript" 2>&1); rc=$? ;;
    esac

    if [ $rc -eq 0 ] && echo "$result" | grep -q "^PASS"; then
        printf "%s\t%s\trun\tPASS\t\n" "$lang" "$case_id" >> "$summary"
        return 0
    fi
    local e
    e=$(echo "$result" | head -3 | tr '\n' '|' | head -c 220)
    printf "%s\t%s\trun\tFAIL\t%s\n" "$lang" "$case_id" "$e" >> "$summary"
    return 1
}

# Batch pre-passes — same shape as run_nested.sh.
batch_kotlin() {
    local kt_files=""
    for case_file in "$CASES_DIR"/*.fkt; do
        [ -f "$case_file" ] || continue
        should_run_case "$lang" "$case_file" || continue
        local case_id
        case_id=$(basename "$case_file" .fkt)
        local out="$OUT_DIR/kotlin/$case_id"
        rm -rf "$out" 2>/dev/null
        mkdir -p "$out"
        if ! "$FRAMEC" compile -l kotlin -o "$out" "$case_file" >"$LOG_DIR/kotlin-$case_id.transpile" 2>&1; then
            local e
            e=$(head -3 "$LOG_DIR/kotlin-$case_id.transpile" | tr '\n' '|' | head -c 220)
            printf "kotlin\t%s\ttranspile\tFAIL\t%s\n" "$case_id" "$e" >> "$summary"
            continue
        fi
        local kt
        kt=$(ls "$out"/*.kt 2>/dev/null | head -1)
        [ -n "$kt" ] && kt_files="$kt_files $kt"
    done
    if [ -n "$kt_files" ]; then
        local jar="$OUT_DIR/kotlin/all.jar"
        local err_log="$LOG_DIR/kotlin-batch.err"
        # Iterative batch: if some files fail to compile (e.g. D1
        # mid-expression-guard bugs in dom-LHS cases), drop them from
        # the list and retry. Each iteration removes failing files
        # parsed from kotlinc's stderr ("path/to/file.kt:NN:NN: error").
        # Capped at 5 iterations — beyond that something else is wrong.
        # Kotlinc default heap OOMs on ~460 files at once. Pass
        # -J-Xmx8g directly (the kotlinc wrapper doesn't reliably
        # honor KOTLIN_OPTS on macos).
        local iter=0
        while [ "$iter" -lt 5 ]; do
            # shellcheck disable=SC2086
            if kotlinc -J-Xmx8g $kt_files -include-runtime -d "$jar" >"$err_log" 2>&1; then
                export KOTLIN_BATCH_JAR="$jar"
                break
            fi
            # Identify failing files from stderr.
            local failed
            failed=$(grep -oE "$OUT_DIR/kotlin/[^/]+/[^.]+\.kt" "$err_log" | sort -u)
            if [ -z "$failed" ]; then
                # No file paths in error — irrecoverable.
                break
            fi
            local new_kt_files=""
            for f in $kt_files; do
                if ! echo "$failed" | grep -qF "$f"; then
                    new_kt_files="$new_kt_files $f"
                fi
            done
            if [ "$new_kt_files" = "$kt_files" ]; then
                break  # no change in list, stop
            fi
            kt_files=$new_kt_files
            iter=$((iter + 1))
        done
    fi
}

# Java batched compile. Each test source has `package nf_<id>;` so a
# single javac invocation produces `<classes>/nf_<id>/Driver.class`
# for every test. Per-test execution then needs only one javac startup
# total (vs ~700ms × N for the per-case path).
#
# Iterative drop-and-retry mirrors batch_kotlin: when a test source
# has a codegen bug (e.g., D1 cascade) javac fails. Parse stderr for
# failing files, drop them, retry. Capped at 5 iterations.
batch_java() {
    local java_files=""
    for case_file in "$CASES_DIR"/*.fjava; do
        [ -f "$case_file" ] || continue
        should_run_case java "$case_file" || continue
        local case_id
        case_id=$(basename "$case_file" .fjava)
        local out="$OUT_DIR/java/$case_id"
        rm -rf "$out" 2>/dev/null
        mkdir -p "$out"
        if ! "$FRAMEC" compile -l java -o "$out" "$case_file" >"$LOG_DIR/java-$case_id.transpile" 2>&1; then
            local e
            e=$(head -3 "$LOG_DIR/java-$case_id.transpile" | tr '\n' '|' | head -c 220)
            printf "java\t%s\ttranspile\tFAIL\t%s\n" "$case_id" "$e" >> "$summary"
            continue
        fi
        local jv
        jv=$(ls "$out"/*.java 2>/dev/null | head -1)
        if [ -n "$jv" ]; then
            # Inject `package nf_<id>;` at the top of the framec .java
            # output. Java requires `package` to be the first non-
            # comment statement; framec emits `import java.util.*;`
            # before any user prolog so we can't route this through
            # the Frame source. sed-prepend is local to batch_java.
            local tmp="$jv.tmp"
            { printf "package nf_%s;\n\n" "$case_id"; cat "$jv"; } > "$tmp" && mv "$tmp" "$jv"
            java_files="$java_files $jv"
        fi
    done
    if [ -n "$java_files" ]; then
        local classes_dir="$OUT_DIR/java/_batch/classes"
        rm -rf "$classes_dir" 2>/dev/null
        mkdir -p "$classes_dir"
        local err_log="$LOG_DIR/java-batch.err"
        local iter=0
        while [ "$iter" -lt 5 ]; do
            # shellcheck disable=SC2086
            if javac -d "$classes_dir" $java_files >"$err_log" 2>&1; then
                export JAVA_BATCH_CLASSES="$classes_dir"
                break
            fi
            local failed
            failed=$(grep -oE "$OUT_DIR/java/[^/]+/[^.]+\.java" "$err_log" | sort -u)
            if [ -z "$failed" ]; then
                break
            fi
            local new_java_files=""
            for f in $java_files; do
                if ! echo "$failed" | grep -qF "$f"; then
                    new_java_files="$new_java_files $f"
                fi
            done
            if [ "$new_java_files" = "$java_files" ]; then
                break
            fi
            java_files=$new_java_files
            iter=$((iter + 1))
        done
    fi
}

batch_csharp() {
    local proj_dir="$OUT_DIR/csharp/_batch/proj"
    rm -rf "$proj_dir" 2>/dev/null
    mkdir -p "$proj_dir"

    local case_ids=""
    for case_file in "$CASES_DIR"/*.fcs; do
        [ -f "$case_file" ] || continue
        should_run_case "$lang" "$case_file" || continue
        local case_id
        case_id=$(basename "$case_file" .fcs)
        local tmp_out
        tmp_out=$(mktemp -d)
        if ! "$FRAMEC" compile -l csharp -o "$tmp_out" "$case_file" >"$LOG_DIR/csharp-$case_id.transpile" 2>&1; then
            local e
            e=$(head -3 "$LOG_DIR/csharp-$case_id.transpile" | tr '\n' '|' | head -c 220)
            printf "csharp\t%s\ttranspile\tFAIL\t%s\n" "$case_id" "$e" >> "$summary"
            continue
        fi
        local cs
        cs=$(ls "$tmp_out"/*.cs 2>/dev/null | head -1)
        if [ -n "$cs" ]; then
            cp "$cs" "$proj_dir/${case_id}.cs"
            case_ids="$case_ids $case_id"
        fi
    done
    [ -z "$case_ids" ] && return

    cat > "$proj_dir/Dispatcher.cs" <<DISPATCHER
using System;

public class Dispatcher {
    public static void Main(string[] args) {
DISPATCHER
    for cid in $case_ids; do
        cat >> "$proj_dir/Dispatcher.cs" <<DISP_TEST
        try { nf_${cid}.Driver.Main(); Console.WriteLine("DISP_${cid}: OK"); }
        catch (Exception e) { Console.WriteLine("DISP_${cid}: FAIL: " + e.Message); }
DISP_TEST
    done
    cat >> "$proj_dir/Dispatcher.cs" <<DISPATCHER
    }
}
DISPATCHER

    cat > "$proj_dir/test.csproj" <<CSPROJ
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>disable</Nullable>
    <RootNamespace>PermFuzz</RootNamespace>
    <StartupObject>Dispatcher</StartupObject>
  </PropertyGroup>
</Project>
CSPROJ

    (cd "$proj_dir" && dotnet restore -v q >"$LOG_DIR/csharp-restore.err" 2>&1) || true
    # Iterative build: dotnet build fails fast on first compile error.
    # When some test files have D1-style codegen bugs, parse the build
    # error log for failing case_ids, drop their .cs files, regenerate
    # Dispatcher.cs from the live set, and retry. Capped at 5
    # iterations. Failing case_ids are accumulated so the post-run
    # dispatcher output includes them as FAIL.
    local dispatcher_out="$OUT_DIR/csharp/_batch/dispatcher.out"
    local skipped_ids=""
    # Helper: regenerate Dispatcher.cs from the live set of .cs files
    # in proj_dir (excluding Dispatcher.cs itself).
    regen_dispatcher() {
        local d="$proj_dir/Dispatcher.cs"
        cat > "$d" <<DISP_HDR
using System;

public class Dispatcher {
    public static void Main(string[] args) {
DISP_HDR
        for cs_file in "$proj_dir"/*.cs; do
            local cid
            cid=$(basename "$cs_file" .cs)
            [ "$cid" = "Dispatcher" ] && continue
            cat >> "$d" <<DISP_TEST
        try { nf_${cid}.Driver.Main(); Console.WriteLine("DISP_${cid}: OK"); }
        catch (Exception e) { Console.WriteLine("DISP_${cid}: FAIL: " + e.Message); }
DISP_TEST
        done
        cat >> "$d" <<DISP_FTR
    }
}
DISP_FTR
    }
    local iter=0
    while [ "$iter" -lt 5 ]; do
        if (cd "$proj_dir" && dotnet build -v q -c Release >"$LOG_DIR/csharp-build.err" 2>&1); then
            (cd "$proj_dir" && dotnet run --no-build -c Release -v q 2>&1) > "$dispatcher_out" || true
            for cid in $skipped_ids; do
                printf "DISP_%s: FAIL: build error (D1 cascade)\n" "$cid" >> "$dispatcher_out"
            done
            export CSHARP_BATCH_OUT="$dispatcher_out"
            break
        fi
        # Identify failing case_ids from build err. Paths look like
        # `/path/<case_id>.cs(LINE,COL): error CSnnnn`. Filter out
        # Dispatcher.cs — when a missing namespace error references
        # Dispatcher's lines, that's a knock-on from a dropped case,
        # not a Dispatcher problem itself.
        local failed_ids
        failed_ids=$(grep -oE "[^/]+\.cs\(" "$LOG_DIR/csharp-build.err" \
                     | sed 's/\.cs($//' | sort -u | grep -v '^Dispatcher$')
        if [ -z "$failed_ids" ]; then
            break
        fi
        local removed=0
        for cid in $failed_ids; do
            if [ -f "$proj_dir/${cid}.cs" ]; then
                rm -f "$proj_dir/${cid}.cs"
                skipped_ids="$skipped_ids $cid"
                removed=$((removed + 1))
            fi
        done
        if [ "$removed" -eq 0 ]; then
            break
        fi
        regen_dispatcher
        iter=$((iter + 1))
    done
}

total=0
passed=0

# Per-lang work as a function so we can fork it for parallel execution.
# Each invocation is fully self-contained: writes only to its own
# `summary_$lang.tsv` (per-lang summary infra prevents races).
process_lang() {
    local lang=$1
    local summary="$PER_LANG_LOG_DIR/summary_$lang.tsv"
    local ext
    ext=$(lang_to_ext "$lang")
    if [ "$lang" = "kotlin" ]; then batch_kotlin; fi
    if [ "$lang" = "csharp" ]; then batch_csharp; fi
    if [ "$lang" = "java" ]; then batch_java; fi
    for case_file in "$CASES_DIR"/*."$ext"; do
        [ -f "$case_file" ] || continue
        should_run_case "$lang" "$case_file" || continue
        run_one "$lang" "$case_file" || true
    done
    if [ "$lang" = "kotlin" ]; then unset KOTLIN_BATCH_JAR; fi
    if [ "$lang" = "csharp" ]; then unset CSHARP_BATCH_OUT; fi
    if [ "$lang" = "java" ]; then unset JAVA_BATCH_CLASSES; fi
}

# Parallelization policy:
#   smoke tier: fork one worker per lang (max ~17 concurrent). Smoke
#     corpora are small (~30-90 cases/lang) so resource pressure is
#     bounded. Drops total wall clock from ~10 min serial to ~1-2 min
#     parallel — the "fast iteration" goal of the smoke tier.
#   full tier: serial. Full tier has 460+ cases/lang × 17 langs =
#     7,820+ cases. Running 17 langs concurrent saturates RAM
#     (kotlinc batch alone can hit 8GB). Serial keeps memory stable
#     while accepting longer wall clock.
RUN_PARALLEL="no"
if [ "$TIER" = "smoke" ] || [ "$TIER" = "core" ]; then
    RUN_PARALLEL="yes"
fi

if [ "$RUN_PARALLEL" = "yes" ]; then
    for lang in $LANGS; do
        process_lang "$lang" &
    done
    wait
else
    for lang in $LANGS; do
        process_lang "$lang"
    done
fi

# Tally PASS/FAIL from the per-lang summary files.
for ln in $LANGS; do
    f="$PER_LANG_LOG_DIR/summary_$ln.tsv"
    [ -f "$f" ] || continue
    while IFS=$'\t' read -r _ _ _ result _; do
        [ "$result" = "PASS" ] && passed=$((passed + 1))
        [ "$result" = "PASS" ] || [ "$result" = "FAIL" ] && total=$((total + 1))
    done < <(tail -n +2 "$f")
done

# Rebuild aggregate summary.tsv from per-lang files in scope.
{
    printf "lang\tcase\tstage\tresult\terror\n"
    for ln in $LANGS; do
        f="$PER_LANG_LOG_DIR/summary_$ln.tsv"
        [ -f "$f" ] && tail -n +2 "$f"
    done
} > "$LOG_DIR/summary.tsv"

echo ""
echo "# arith [$TIER]: $passed / $total passed"
for ln in $LANGS; do
    f="$PER_LANG_LOG_DIR/summary_$ln.tsv"
    [ -f "$f" ] || continue
    awk -F'\t' '$4 == "FAIL" {print "  not ok " $1 "/" $2 ": " $5}' "$f"
done

if [ "$passed" -ne "$total" ]; then
    exit 1
fi
exit 0
