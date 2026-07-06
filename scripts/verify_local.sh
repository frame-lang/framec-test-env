#!/usr/bin/env bash
# verify_local.sh — verify a Frame fixture (or several) end-to-end on the
# host: framec transpile → native compile → run → check PASS, for the
# backend implied by each file's extension.
#
# This is the local counterpart to the Docker matrix. The stock
# tests/run_single_test.sh is Docker-oriented and assumes each language's
# JSON/runtime deps are already wired inside the container; on a bare host
# they aren't. This script provisions the missing pieces once (idempotent,
# cached under output/.verify_local/) and reports per file:
#
#   PASS[<ext>] <name>            transpiled, compiled and ran clean
#   FAIL[<ext>] <name> :: <why>   transpile/compile/run failed
#   SKIP[<ext>] <name> :: <why>   toolchain or dep unavailable on this host
#
# Deps it discovers / provisions (skips the backend if it truly can't):
#   rust    serde+serde_json+tokio+futures cargo crate
#   java    Jackson (~/.m2) + org.json (~/.m2 or downloaded)
#   kotlin  Jackson + kotlinx-coroutines (~/.gradle) + org.json
#   csharp  a net10.0 console project
#   c/cpp   cjson / nlohmann headers (Homebrew), arm64 on Apple Silicon
#   ts      tsx (PATH or npx)   ·   lua persist   serpent (if present)
#
# Erlang (`ferl`) is deprecated and reported as SKIP.
#
# Usage:
#   scripts/verify_local.sh tests/.../dict_ops.frs [more files...]
#   scripts/verify_local.sh tests/common/positive/data_types/dict_ops.*   # a whole stem
#   FRAMEC=/path/to/framec scripts/verify_local.sh <file>

set -o pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRAMEC="${FRAMEC:-$(command -v framec 2>/dev/null)}"
CACHE="$ROOT/output/.verify_local"
# Force arm64 on Apple Silicon *hardware* — detect via sysctl, not `uname -m`,
# which reports x86_64 under a Rosetta shell and would then mismatch the arm64
# Homebrew libs (cjson) at link time.
ARCH_FLAG=""
[ "$(uname -s)" = "Darwin" ] && [ "$(sysctl -n hw.optional.arm64 2>/dev/null)" = "1" ] && ARCH_FLAG="-arch arm64"

if [ -z "$FRAMEC" ] || [ ! -x "$FRAMEC" ]; then
    echo "verify_local: framec not found (set FRAMEC=/path/to/framec)" >&2; exit 2
fi
mkdir -p "$CACHE"

have() { command -v "$1" >/dev/null 2>&1; }
first_jar() { find "$@" 2>/dev/null | head -1; }

# --- dependency discovery / provisioning (all idempotent) ---
jackson_cp() {
    local m="$HOME/.m2/repository/com/fasterxml/jackson"
    local db co an
    db=$(first_jar "$m/core/jackson-databind" -name 'jackson-databind-*.jar')
    co=$(first_jar "$m/core/jackson-core" -name 'jackson-core-*.jar')
    an=$(first_jar "$m/core/jackson-annotations" -name 'jackson-annotations-*.jar')
    [ -n "$db" ] && [ -n "$co" ] && [ -n "$an" ] && echo "$db:$co:$an"
}
orgjson_jar() {
    local j; j=$(first_jar "$HOME/.m2/repository/org/json/json" -name 'json-*.jar')
    [ -n "$j" ] && { echo "$j"; return; }
    j="$CACHE/org.json.jar"
    [ -f "$j" ] && { echo "$j"; return; }
    have curl && curl -fsSL -o "$j" \
        "https://repo1.maven.org/maven2/org/json/json/20231013/json-20231013.jar" 2>/dev/null \
        && echo "$j"
}
coroutines_jar() { first_jar "$HOME/.gradle" -name 'kotlinx-coroutines-core-jvm-*.jar'; }
ensure_rust_crate() {
    local rc="$CACHE/rustcrate"
    [ -f "$rc/Cargo.toml" ] && { echo "$rc"; return; }
    mkdir -p "$rc/src/bin"
    printf '[package]\nname="vpkg"\nversion="0.0.0"\nedition="2021"\n[dependencies]\nserde={version="1",features=["derive"]}\nserde_json="1"\ntokio={version="1",features=["full"]}\nfutures="0.3"\n' > "$rc/Cargo.toml"
    # single binary `v` from src/bin/v.rs — no src/main.rs (would collide).
    echo "$rc"
}
ensure_csproj() {
    local cp="$CACHE/csproj"
    [ -f "$cp/v.csproj" ] && { echo "$cp"; return; }
    mkdir -p "$cp"
    printf '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework><Nullable>disable</Nullable><AssemblyName>v</AssemblyName></PropertyGroup></Project>\n' > "$cp/v.csproj"
    echo "$cp"
}

# Per the project convention (tests/writing-tests): success is a clean exit
# (rc 0) with a PASS/ok line OR no output at all; failure is a non-zero exit or
# an explicit failure marker in the output.
passed() {
    local rc="$1" out="$2"
    [ "$rc" -eq 0 ] || return 1
    echo "$out" | grep -qE "not ok|FAIL|Traceback \(most|panicked|Exception in thread" && return 1
    return 0
}

# report <line> — print and clean the caller's $W (dynamically scoped).
report() { echo "$1"; rm -rf "$W"; }

verify_one() {
    local f="$1" ext="${1##*.}" name W target
    name="$(basename "$f" ".$ext")"; W="$(mktemp -d)"
    case "$ext" in
        fpy) target=python_3;; fts) target=typescript;; fjs) target=javascript;;
        frs) target=rust;; fc) target=c;; fcpp) target=cpp_23;; fcs) target=csharp;;
        fjava) target=java;; fgo) target=go;; fphp) target=php;; fkt) target=kotlin;;
        fswift) target=swift;; frb) target=ruby;; flua) target=lua;; fdart) target=dart;;
        fgd) target=gdscript;; ferl) report "SKIP[ferl] $name :: Erlang deprecated"; return;;
        *) report "SKIP[$ext] $name :: unknown extension"; return;;
    esac
    if ! "$FRAMEC" compile -l "$target" -o "$W" "$f" >"$W/t" 2>&1; then
        report "FAIL[$ext] $name :: transpile: $(grep -iE 'error|E[0-9]{3}' "$W/t" | head -1 | cut -c1-70)"; return
    fi
    local out rc=0 g
    case "$ext" in
        fpy)  have python3 || { report "SKIP[$ext] $name :: no python3"; return; }
              out=$(python3 "$W/$name.py" 2>&1); rc=$? ;;
        fjs)  have node || { report "SKIP[$ext] $name :: no node"; return; }
              cp "$W/$name.js" "$W/m.mjs"; out=$(node "$W/m.mjs" 2>&1); rc=$? ;;
        fts)  if have tsx; then out=$(tsx "$W/$name.ts" 2>&1); rc=$?
              elif have npx; then out=$(cd "$W" && npx --yes tsx "$name.ts" 2>&1); rc=$?
              else report "SKIP[$ext] $name :: no tsx/npx"; return; fi ;;
        fgo)  have go || { report "SKIP[$ext] $name :: no go"; return; }
              out=$(cd "$W" && GOFLAGS=-count=1 go run "$name.go" 2>&1); rc=$? ;;
        fphp) have php || { report "SKIP[$ext] $name :: no php"; return; }
              out=$(php "$W/$name.php" 2>&1); rc=$? ;;
        frb)  have ruby || { report "SKIP[$ext] $name :: no ruby"; return; }
              out=$(ruby "$W/$name.rb" 2>&1); rc=$? ;;
        flua) have lua || { report "SKIP[$ext] $name :: no lua"; return; }
              out=$(lua "$W/$name.lua" 2>&1); rc=$?
              echo "$out" | grep -q "module 'serpent'" && { report "SKIP[$ext] $name :: lua serpent module not installed"; return; } ;;
        fdart) have dart || { report "SKIP[$ext] $name :: no dart"; return; }
              out=$(dart run "$W/$name.dart" 2>&1); rc=$? ;;
        fgd)  have godot || { report "SKIP[$ext] $name :: no godot"; return; }
              out=$(godot --headless --script "$W/$name.gd" 2>&1); rc=$? ;;
        fswift) have swiftc || { report "SKIP[$ext] $name :: no swiftc"; return; }
              if swiftc -o "$W/b" "$W/$name.swift" 2>"$W/c"; then out=$("$W/b" 2>&1); rc=$?
              else report "FAIL[$ext] $name :: compile: $(grep -m1 error "$W/c" | cut -c1-70)"; return; fi ;;
        fc)   have gcc || { report "SKIP[$ext] $name :: no gcc"; return; }
              # Prefer /opt/homebrew (arm64) over /usr/local (often x86_64) so
              # the lib arch matches an arm64 object on Apple Silicon.
              local inc=""
              [ -d /opt/homebrew/include/cjson ] && inc=/opt/homebrew
              [ -z "$inc" ] && [ -d /usr/local/include/cjson ] && inc=/usr/local
              [ -n "$inc" ] || { report "SKIP[$ext] $name :: cjson not installed (brew install cjson)"; return; }
              if gcc $ARCH_FLAG -o "$W/b" "$W/$name.c" -I$inc/include -L$inc/lib -lcjson 2>"$W/c"; then out=$("$W/b" 2>&1); rc=$?
              else report "FAIL[$ext] $name :: compile: $(grep -m1 -i error "$W/c" | cut -c1-70)"; return; fi ;;
        fcpp) have g++ || { report "SKIP[$ext] $name :: no g++"; return; }
              local cinc=""
              [ -d /opt/homebrew/include/nlohmann ] && cinc=/opt/homebrew
              [ -z "$cinc" ] && [ -d /usr/local/include/nlohmann ] && cinc=/usr/local
              [ -n "$cinc" ] || { report "SKIP[$ext] $name :: nlohmann-json not installed"; return; }
              if g++ $ARCH_FLAG -std=c++20 -I$cinc/include -o "$W/b" "$W/$name.cpp" 2>"$W/c"; then out=$("$W/b" 2>&1); rc=$?
              else report "FAIL[$ext] $name :: compile: $(grep -m1 -iE 'error|fatal' "$W/c" | cut -c1-70)"; return; fi ;;
        fjava) have javac || { report "SKIP[$ext] $name :: no javac"; return; }
              local jcp oj; jcp=$(jackson_cp); oj=$(orgjson_jar)
              [ -n "$jcp" ] || { report "SKIP[$ext] $name :: Jackson not in ~/.m2"; return; }
              local cp="$jcp"; [ -n "$oj" ] && cp="$jcp:$oj"
              if javac -cp "$cp" -d "$W/o" "$W"/*.java 2>"$W/c"; then out=$(java -cp "$W/o:$cp" Main 2>&1); rc=$?
              else report "FAIL[$ext] $name :: compile: $(grep -m1 error "$W/c" | cut -c1-70)"; return; fi ;;
        fkt)  have kotlinc || { report "SKIP[$ext] $name :: no kotlinc"; return; }
              local jcp co oj; jcp=$(jackson_cp); co=$(coroutines_jar); oj=$(orgjson_jar)
              [ -n "$jcp" ] || { report "SKIP[$ext] $name :: Jackson not in ~/.m2"; return; }
              local cp="$jcp"; [ -n "$co" ] && cp="$cp:$co"; [ -n "$oj" ] && cp="$cp:$oj"
              if kotlinc -cp "$cp" "$W/$name.kt" -include-runtime -d "$W/app.jar" >"$W/c" 2>&1; then
                  local km; km=$(unzip -p "$W/app.jar" META-INF/MANIFEST.MF 2>/dev/null | grep Main-Class | sed 's/Main-Class: *//' | tr -d '\r')
                  out=$(java -cp "$W/app.jar:$cp" "$km" 2>&1); rc=$?
              else report "FAIL[$ext] $name :: compile: $(grep -m1 -i error "$W/c" | cut -c1-70)"; return; fi ;;
        fcs)  have dotnet || { report "SKIP[$ext] $name :: no dotnet"; return; }
              local cp; cp=$(ensure_csproj); rm -f "$cp"/*.cs; cp "$W"/*.cs "$cp/"
              out=$(cd "$cp" && dotnet run -c Release 2>&1); rc=$? ;;
        frs)  have cargo || { report "SKIP[$ext] $name :: no cargo"; return; }
              local rc_dir; rc_dir=$(ensure_rust_crate); cp "$W/$name.rs" "$rc_dir/src/bin/v.rs"
              out=$(cd "$rc_dir" && cargo run --release --bin v 2>"$W/c"); rc=$?
              [ $rc -ne 0 ] && out="$out $(grep -m2 'error\[' "$W/c" | tr '\n' ' ')" ;;
    esac
    if passed "$rc" "$out"; then report "PASS[$ext] $name"
    else report "FAIL[$ext] $name :: run (rc=$rc): $(echo "$out" | tail -2 | tr '\n' ' ' | cut -c1-90)"; fi
}

[ $# -eq 0 ] && { grep -m20 '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0; }
rc=0
for f in "$@"; do
    [ -f "$f" ] || { echo "SKIP :: not a file: $f"; continue; }
    # helper/sidecar files are not fixtures — skip silently
    case "$f" in *.driver|*.driver.escript|*.escript|*.md|*.txt|*/README) continue ;; esac
    r=$(verify_one "$f"); echo "$r"
    echo "$r" | grep -q '^FAIL' && rc=1
done
exit $rc
