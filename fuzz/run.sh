#!/usr/bin/env bash
#
# Runs fuzz cases (from gen.py) through framec and then the target
# language's parser/compiler. The goal is to surface framec codegen bugs,
# so we do syntax+semantic checks without linking/running (fast feedback).
#
# Per case we write one row to logs/summary.tsv with columns:
#   lang  case  stage  result  error_head
# where stage is "transpile" or "compile" and result is PASS, FAIL, or
# SKIP_NO_TOOLCHAIN.
#
# Negative cases (Phase 8): a case file whose prolog contains
#   # @@expect-error: E113
# is expected to be REJECTED by framec with that error code. Mismatch
# (transpile succeeded, or wrong code) is FAIL; matching rejection is
# PASS. Phase 8 cases skip the language-toolchain compile step.
#
# Usage:
#   ./run.sh                         # all languages
#   ./run.sh python_3 rust           # a subset
#   TRANSPILE_ONLY=1 ./run.sh        # skip compile step
#
# Environment:
#   FRAMEC  path to framec binary (default: ../../framepiler/target/release/framec)

set -o pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
FRAMEC=${FRAMEC:-$(cd "$SCRIPT_DIR/../../framepiler" 2>/dev/null && pwd)/target/release/framec}
if [ ! -x "$FRAMEC" ]; then
    FRAMEC=/Users/marktruluck/projects/framepiler/target/release/framec
fi

CASES_DIR=$SCRIPT_DIR/cases
OUT_DIR=$SCRIPT_DIR/out
LOG_DIR=$SCRIPT_DIR/logs
mkdir -p "$OUT_DIR" "$LOG_DIR"

TRANSPILE_ONLY=${TRANSPILE_ONLY:-0}

LANGS=${@:-"python_3 typescript javascript rust c cpp_23 csharp java go php kotlin swift ruby erlang lua dart gdscript"}

summary_file=$LOG_DIR/summary.tsv
: > "$summary_file"
printf "lang\tcase\tstage\tresult\terror\n" >> "$summary_file"

lang_to_ext() {
    case "$1" in
        python_3)   echo fpy ;;
        typescript) echo fts ;;
        javascript) echo fjs ;;
        rust)       echo frs ;;
        c)          echo fc ;;
        cpp_23)     echo fcpp ;;
        csharp)     echo fcs ;;
        java)       echo fjava ;;
        go)         echo fgo ;;
        php)        echo fphp ;;
        kotlin)     echo fkt ;;
        swift)      echo fswift ;;
        ruby)       echo frb ;;
        erlang)     echo ferl ;;
        lua)        echo flua ;;
        dart)       echo fdart ;;
        gdscript)   echo fgd ;;
    esac
}

# Compile/parse-check per language. 0 = pass, 1 = fail, 77 = skip (no tool).
compile_check() {
    local lang=$1
    local genfile=$2
    local out=$3
    local errlog=$4

    case "$lang" in
        python_3)
            python3 -c "import ast; ast.parse(open('$genfile').read())" > "$errlog" 2>&1
            ;;

        gdscript)
            # GDScript needs Godot. Skip if not available.
            if command -v godot >/dev/null 2>&1; then
                godot --headless --check-only --script "$genfile" > "$errlog" 2>&1
            else
                echo "no godot" > "$errlog"; return 77
            fi
            ;;

        typescript)
            if command -v tsc >/dev/null 2>&1; then
                tsc --noEmit --skipLibCheck --target es2020 --module es2020 \
                    --strict false --noImplicitAny false --allowJs \
                    "$genfile" > "$errlog" 2>&1
            else
                echo "no tsc" > "$errlog"; return 77
            fi
            ;;

        javascript)
            local mjs="${genfile%.js}.mjs"
            cp "$genfile" "$mjs"
            node --check "$mjs" 2>"$errlog"
            ;;

        rust)
            rustc --edition 2021 --crate-type=lib -o "$out/lib.rlib" \
                  "$genfile" 2>"$errlog"
            ;;

        c)
            gcc -c -o /dev/null "$genfile" 2>"$errlog"
            ;;

        cpp_23)
            g++ -std=c++2a -c -o /dev/null "$genfile" 2>"$errlog"
            ;;

        csharp)
            if ! command -v dotnet >/dev/null 2>&1; then
                echo "no dotnet" > "$errlog"; return 77
            fi
            # Reuse a single classlib probe across all cases — `dotnet build`
            # is ~20 sec cold-start and ~0.3 sec warm; creating one probe per
            # case would be a lifetime.
            local pdir="$OUT_DIR/_csharp_probe"
            if [ ! -f "$pdir/fuzz_probe.csproj" ]; then
                mkdir -p "$pdir"
                (cd "$pdir" && dotnet new classlib -o . --force >/dev/null 2>&1) \
                    || { echo "dotnet new failed" > "$errlog"; return 1; }
                rm -f "$pdir/Class1.cs"
                # Warm the build cache once.
                dotnet build "$pdir" --nologo -v q > /dev/null 2>&1 || true
            fi
            cp "$genfile" "$pdir/Fuzz.cs"
            dotnet build "$pdir" --nologo -v q --no-restore > "$errlog" 2>&1
            rm -f "$pdir/Fuzz.cs"
            ;;

        java)
            local cls_dir="$out/cls"
            mkdir -p "$cls_dir"
            javac -d "$cls_dir" "$genfile" 2>"$errlog"
            ;;

        go)
            local gdir="$out/gomod"
            mkdir -p "$gdir"
            [ -f "$gdir/go.mod" ] || (cd "$gdir" && go mod init fuzz >/dev/null 2>&1)
            cp "$genfile" "$gdir/main.go"
            (cd "$gdir" && go vet .) > "$errlog" 2>&1
            ;;

        php)
            php -l "$genfile" > "$errlog" 2>&1
            ;;

        kotlin)
            if ! command -v kotlinc >/dev/null 2>&1; then
                echo "no kotlinc" > "$errlog"; return 77
            fi
            kotlinc -d "$out/classes" "$genfile" > "$errlog" 2>&1
            ;;

        swift)
            swiftc -parse "$genfile" 2>"$errlog"
            ;;

        ruby)
            ruby -c "$genfile" > "$errlog" 2>&1
            ;;

        erlang)
            local mod
            mod=$(grep -m1 '^-module(' "$genfile" | sed 's/-module(\(.*\))\./\1/')
            if [ -z "$mod" ]; then
                echo "no -module directive" > "$errlog"; return 1
            fi
            local target_erl="$out/${mod}.erl"
            cp "$genfile" "$target_erl"
            (cd "$out" && erlc "$target_erl") 2>"$errlog"
            ;;

        lua)
            luac -p "$genfile" 2>"$errlog"
            ;;

        dart)
            dart analyze "$genfile" > "$errlog" 2>&1
            if grep -q "^ *error" "$errlog"; then return 1; fi
            return 0
            ;;

        *)
            echo "unknown lang: $lang" > "$errlog"; return 1
            ;;
    esac
}

# Languages whose compile-check we batch into a single tool invocation.
# Per-file cold start dominates wall-clock for these (kotlin, tsc, javac,
# dotnet build all pay 0.5-5s of JVM/.NET/TS startup each). Each tool
# accepts a list of source files and produces error lines that include
# the file path, so we can parse per-file pass/fail from one
# whole-corpus invocation.
is_batchable() {
    case "$1" in
        kotlin|typescript|java|csharp) return 0 ;;
        *) return 1 ;;
    esac
}

# Read the per-case `# @@expect-error: <CODE>` directive (Phase 8
# negative-test convention). Returns the bare code (e.g. E113) on
# stdout, or empty if the case is positive (no directive). Looks
# only at the first 10 lines so the prolog scan is cheap. Uses
# POSIX bracket classes ([[:space:]]) since `\s` isn't portable to
# BSD sed (macOS dev hosts).
read_expected_error() {
    local case_file=$1
    head -10 "$case_file" 2>/dev/null \
        | grep -m1 -oE '@@expect-error:[[:space:]]*E[0-9]+' \
        | sed 's/.*expect-error:[[:space:]]*//'
}

# Transpile one case via framec. Writes the genfile path to stdout on
# success (so the caller can collect it). Writes a TRANSPILE_FAIL or
# NO_OUTPUT row to summary_file on failure and returns 1.
#
# Negative-test convention: if the case's prolog declares
# `# @@expect-error: <CODE>`, transpile is expected to fail with that
# code. Inverted classification:
#   transpile-FAIL with matching code     → PASS  (return 2 = positive_done)
#   transpile-FAIL with different code    → FAIL  (wrong error)
#   transpile succeeds                    → FAIL  (expected rejection)
# Return 2 signals "case fully handled, do NOT continue to compile-check"
# so the caller skips the language-toolchain step.
transpile_case() {
    local lang=$1
    local case_file=$2
    local case_id=$(basename "$case_file" | sed 's/\.f[a-z]*$//')
    local out="$OUT_DIR/$lang/$case_id"
    rm -rf "$out" 2>/dev/null
    mkdir -p "$out"
    local errlog="$LOG_DIR/$lang-$case_id.err"

    local expected_err
    expected_err=$(read_expected_error "$case_file")

    if ! "$FRAMEC" compile -l "$lang" -o "$out" "$case_file" > "$errlog" 2>&1; then
        local err=$(head -3 "$errlog" | grep -v frame_runtime | tr '\n' '|' | head -c 220)
        if [ -n "$expected_err" ]; then
            # Negative case: a transpile failure is expected.
            if grep -qE "\b${expected_err}\b" "$errlog"; then
                printf "%s\t%s\ttranspile\tPASS\texpected %s\n" \
                    "$lang" "$case_id" "$expected_err" >> "$summary_file"
                return 2
            fi
            printf "%s\t%s\ttranspile\tFAIL\texpected %s, got: %s\n" \
                "$lang" "$case_id" "$expected_err" "$err" >> "$summary_file"
            return 1
        fi
        printf "%s\t%s\ttranspile\tFAIL\t%s\n" "$lang" "$case_id" "$err" >> "$summary_file"
        return 1
    fi
    if [ -n "$expected_err" ]; then
        # Negative case but transpile succeeded — the expected
        # rejection didn't happen. That's a regression in the
        # validator (E... no longer fires) or the case generator
        # is wrong. Either way, fail loudly.
        printf "%s\t%s\ttranspile\tFAIL\texpected %s but transpile succeeded\n" \
            "$lang" "$case_id" "$expected_err" >> "$summary_file"
        return 1
    fi
    local genfile
    genfile=$(ls "$out"/*.* 2>/dev/null | grep -v '\.log$\|\.err$' | head -1)
    if [ -z "$genfile" ]; then
        printf "%s\t%s\ttranspile\tNO_OUTPUT\t\n" "$lang" "$case_id" >> "$summary_file"
        return 1
    fi
    echo "$genfile"
    return 0
}

# Per-case compile-check (used for non-batchable languages).
run_case() {
    local lang=$1
    local case_file=$2
    local case_id=$(basename "$case_file" | sed 's/\.f[a-z]*$//')
    local out="$OUT_DIR/$lang/$case_id"
    local errlog="$LOG_DIR/$lang-$case_id.err"

    local genfile
    genfile=$(transpile_case "$lang" "$case_file")
    local trc=$?
    # Return code 2 = negative-case classified as PASS by transpile_case;
    # there's no genfile to compile-check, so we're done.
    if [ $trc -eq 2 ]; then
        return 0
    fi
    if [ $trc -ne 0 ]; then
        return 1
    fi

    if [ "$TRANSPILE_ONLY" = "1" ]; then
        printf "%s\t%s\ttranspile\tPASS\t\n" "$lang" "$case_id" >> "$summary_file"
        return 0
    fi

    compile_check "$lang" "$genfile" "$out" "$errlog"
    local rc=$?
    if [ $rc -eq 77 ]; then
        printf "%s\t%s\tcompile\tSKIP_NO_TOOLCHAIN\t\n" "$lang" "$case_id" >> "$summary_file"
        return 0
    fi
    if [ $rc -ne 0 ]; then
        local err=$(head -3 "$errlog" | tr '\n' '|' | head -c 220)
        printf "%s\t%s\tcompile\tFAIL\t%s\n" "$lang" "$case_id" "$err" >> "$summary_file"
        return 1
    fi
    printf "%s\t%s\tok\tPASS\t\n" "$lang" "$case_id" >> "$summary_file"
    return 0
}

# Run a single batch compile-check for a language. genfiles is a
# newline-separated list of transpiled output paths. Writes a
# per-case row to summary_file for each genfile based on whether
# the batch errlog mentions that file path.
run_batch() {
    local lang=$1
    local genfiles_list=$2  # newline-separated paths
    local batch_errlog="$LOG_DIR/$lang-batch.err"

    if [ -z "$genfiles_list" ]; then
        return 0
    fi

    # Run the language-appropriate batched compile.
    case "$lang" in
        kotlin)
            if ! command -v kotlinc >/dev/null 2>&1; then
                echo "$lang: SKIP (no kotlinc)"
                while IFS= read -r f; do
                    [ -z "$f" ] && continue
                    local cid=$(basename "$f" | sed 's/\.[a-z]*$//')
                    printf "%s\t%s\tcompile\tSKIP_NO_TOOLCHAIN\t\n" "$lang" "$cid" >> "$summary_file"
                done <<< "$genfiles_list"
                return 0
            fi
            mkdir -p "$OUT_DIR/_kotlin_classes"
            # Pass all files; kotlinc treats them as one compilation unit
            # (each file has its own top-level class, so no symbol
            # collisions). Errors are: <file>:<line>:<col>: error: <msg>
            echo "$genfiles_list" | xargs kotlinc -d "$OUT_DIR/_kotlin_classes" \
                > "$batch_errlog" 2>&1
            ;;
        typescript)
            if ! command -v tsc >/dev/null 2>&1; then
                echo "$lang: SKIP (no tsc)"
                while IFS= read -r f; do
                    [ -z "$f" ] && continue
                    local cid=$(basename "$f" | sed 's/\.[a-z]*$//')
                    printf "%s\t%s\tcompile\tSKIP_NO_TOOLCHAIN\t\n" "$lang" "$cid" >> "$summary_file"
                done <<< "$genfiles_list"
                return 0
            fi
            # tsc emits errors as: <file>(line,col): error TS<n>: <msg>
            echo "$genfiles_list" | xargs tsc --noEmit --skipLibCheck \
                --target es2020 --module es2020 \
                --strict false --noImplicitAny false --allowJs \
                > "$batch_errlog" 2>&1
            ;;
        java)
            if ! command -v javac >/dev/null 2>&1; then
                echo "$lang: SKIP (no javac)"
                while IFS= read -r f; do
                    [ -z "$f" ] && continue
                    local cid=$(basename "$f" | sed 's/\.[a-z]*$//')
                    printf "%s\t%s\tcompile\tSKIP_NO_TOOLCHAIN\t\n" "$lang" "$cid" >> "$summary_file"
                done <<< "$genfiles_list"
                return 0
            fi
            mkdir -p "$OUT_DIR/_java_classes"
            # javac error format: <file>:<line>: error: <msg>
            echo "$genfiles_list" | xargs javac -d "$OUT_DIR/_java_classes" \
                2> "$batch_errlog"
            ;;
        csharp)
            if ! command -v dotnet >/dev/null 2>&1; then
                echo "$lang: SKIP (no dotnet)"
                while IFS= read -r f; do
                    [ -z "$f" ] && continue
                    local cid=$(basename "$f" | sed 's/\.[a-z]*$//')
                    printf "%s\t%s\tcompile\tSKIP_NO_TOOLCHAIN\t\n" "$lang" "$cid" >> "$summary_file"
                done <<< "$genfiles_list"
                return 0
            fi
            local pdir="$OUT_DIR/_csharp_probe"
            if [ ! -f "$pdir/fuzz_probe.csproj" ]; then
                mkdir -p "$pdir"
                (cd "$pdir" && dotnet new classlib -o . --force >/dev/null 2>&1) \
                    || { echo "dotnet new failed" > "$batch_errlog"; return 1; }
                rm -f "$pdir/Class1.cs"
                dotnet build "$pdir" --nologo -v q > /dev/null 2>&1 || true
            fi
            # Wipe previous batch's files and copy all fresh ones in.
            find "$pdir" -maxdepth 1 -name "*.cs" -delete 2>/dev/null || true
            while IFS= read -r f; do
                [ -z "$f" ] && continue
                cp "$f" "$pdir/$(basename "$f")"
            done <<< "$genfiles_list"
            # dotnet error format: <file>(line,col): error CS<n>: <msg>
            dotnet build "$pdir" --nologo -v q --no-restore > "$batch_errlog" 2>&1
            # Clean up so the next batch starts fresh.
            find "$pdir" -maxdepth 1 -name "*.cs" -delete 2>/dev/null || true
            ;;
    esac

    # Filter the batch errlog down to *error* lines only. Compilers
    # emit warnings on the same per-file format, but we only fail a
    # case when the compiler emits a real error for it (matches the
    # per-case behavior, which used the compiler's exit code).
    local filtered_errlog="$batch_errlog.errors"
    case "$lang" in
        kotlin)
            # `<file>:<line>:<col>: error: <msg>`
            grep -E ': error: ' "$batch_errlog" > "$filtered_errlog" 2>/dev/null
            ;;
        typescript)
            # `<file>(line,col): error TS<n>: <msg>`
            grep -E '\): error TS' "$batch_errlog" > "$filtered_errlog" 2>/dev/null
            ;;
        java)
            # `<file>:<line>: error: <msg>`
            grep -E ': error: ' "$batch_errlog" > "$filtered_errlog" 2>/dev/null
            ;;
        csharp)
            # `<file>(line,col): error CS<n>: <msg>` — warnings use
            # `warning CS<n>` and must not flag a case as failed.
            grep -E '\): error CS' "$batch_errlog" > "$filtered_errlog" 2>/dev/null
            ;;
    esac

    # Parse per-file results from the filtered errlog. A file failed
    # if any error line mentions its basename; otherwise it passed.
    while IFS= read -r genfile; do
        [ -z "$genfile" ] && continue
        local case_id=$(basename "$(dirname "$genfile")")
        local genbase=$(basename "$genfile")
        if [ -s "$filtered_errlog" ] && grep -qF "$genbase" "$filtered_errlog"; then
            local err
            err=$(grep -F "$genbase" "$filtered_errlog" \
                  | head -3 | tr '\n' '|' | head -c 220)
            printf "%s\t%s\tcompile\tFAIL\t%s\n" "$lang" "$case_id" "$err" >> "$summary_file"
        else
            printf "%s\t%s\tok\tPASS\t\n" "$lang" "$case_id" >> "$summary_file"
        fi
    done <<< "$genfiles_list"
}

for lang in $LANGS; do
    ext=$(lang_to_ext "$lang")
    if [ -z "$ext" ]; then
        echo "skip unknown: $lang"
        continue
    fi
    cases=$(ls "$CASES_DIR/$lang"/case_*.$ext 2>/dev/null | sort)
    total=$(echo "$cases" | grep -c . || echo 0)
    if [ "$total" -eq 0 ]; then
        echo "$lang: no cases in $CASES_DIR/$lang (run gen.py first)"
        continue
    fi
    echo "=== $lang ($total cases) ==="

    if is_batchable "$lang" && [ "$TRANSPILE_ONLY" != "1" ]; then
        # Phase 1: transpile every case (per-case framec invocation —
        # framec is fast). Collect successful genfiles for batch
        # compile-check. Negative cases (rc=2) are already recorded
        # by transpile_case and shouldn't enter the batch.
        genfiles=""
        for case_file in $cases; do
            genfile=$(transpile_case "$lang" "$case_file")
            local trc=$?
            if [ $trc -ne 0 ]; then
                # rc=1 → already-recorded failure; rc=2 → negative-case
                # PASS already recorded. Either way, no genfile.
                continue
            fi
            if [ -n "$genfiles" ]; then
                genfiles="$genfiles
$genfile"
            else
                genfiles="$genfile"
            fi
        done
        # Phase 2: one batched compile-check across all transpiled outputs.
        run_batch "$lang" "$genfiles"
    else
        for case_file in $cases; do
            run_case "$lang" "$case_file" >/dev/null
        done
    fi

    pass=$(awk -v L="$lang" -F'\t' '$1==L && $4=="PASS"{n++} END{print n+0}' "$summary_file")
    fail=$(awk -v L="$lang" -F'\t' '$1==L && $4=="FAIL"{n++} END{print n+0}' "$summary_file")
    skip=$(awk -v L="$lang" -F'\t' '$1==L && $4 ~ /SKIP/{n++} END{print n+0}' "$summary_file")
    echo "$lang: $pass pass / $fail fail / $skip skip"
done

echo ""
echo "=== Failure summary (stage × lang) ==="
awk -F'\t' 'NR>1 && $4=="FAIL" {print $1"  "$3}' "$summary_file" \
    | sort | uniq -c | sort -rn | head -20
