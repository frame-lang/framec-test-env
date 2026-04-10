#!/bin/bash
# Frame Test Environment — Docker Orchestrator
#
# Usage:
#   ./run.sh /path/to/framec                    # Run all 17 languages
#   ./run.sh /path/to/framec --python --rust    # Run specific languages
#   ./run.sh /path/to/framec --clean            # Clean output before running
#   ./run.sh --build                            # Build all images (no run)
#   ./run.sh --compare /path/a /path/b          # Run both, diff results
#
# On macOS, the framec binary must be a Linux binary. Use --build-framec to
# cross-compile from a Rust source directory:
#   ./run.sh --build-framec /path/to/framepiler/repo

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEST_ENV_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
    echo "Usage: $0 [OPTIONS] <framec-binary> [SERVICES...]"
    echo ""
    echo "Options:"
    echo "  --clean              Clean output directories before running"
    echo "  --build              Build all Docker images (no test run)"
    echo "  --build-framec DIR   Cross-compile framec for Linux from source DIR"
    echo "  --compare A B        Run both binaries and diff results"
    echo "  --help               Show this help"
    echo ""
    echo "Services: python typescript javascript rust c cpp csharp java"
    echo "          go php kotlin swift ruby erlang lua dart gdscript"
    echo ""
    echo "Examples:"
    echo "  $0 ./framec-linux                    # Run all tests"
    echo "  $0 ./framec-linux python rust go     # Run specific languages"
    echo "  $0 --clean ./framec-linux            # Clean first, then run"
    echo "  $0 --compare ./old-framec ./new-framec"
}

clean_output() {
    echo "Cleaning output directories..."
    rm -rf "$TEST_ENV_ROOT/output"
    mkdir -p "$TEST_ENV_ROOT/output"
    echo "Clean."
}

build_framec_linux() {
    local src_dir="$1"
    echo "Building framec for Linux from $src_dir..."
    docker run --rm \
        -v "$src_dir:/src:ro" \
        -v "$SCRIPT_DIR:/out" \
        rust:latest \
        bash -c "cp -r /src /build && cd /build && cargo build --release -p framec && cp target/release/framec /out/framec-linux"
    echo "Built: $SCRIPT_DIR/framec-linux"
}

run_tests() {
    local framec_bin="$1"
    shift
    local services="$@"

    # Resolve to absolute path
    framec_bin="$(cd "$(dirname "$framec_bin")" && pwd)/$(basename "$framec_bin")"

    if [ ! -f "$framec_bin" ]; then
        echo "Error: framec binary not found: $framec_bin"
        exit 1
    fi

    # Verify it's a Linux binary (not macOS)
    if file "$framec_bin" | grep -q "Mach-O"; then
        echo "Error: $framec_bin is a macOS binary. Docker requires a Linux binary."
        echo "Use: $0 --build-framec /path/to/source"
        exit 1
    fi

    echo "Running Frame tests..."
    echo "  framec: $framec_bin"
    echo "  services: ${services:-all}"
    echo ""

    cd "$SCRIPT_DIR"
    local env_flags=""
    if [ "${DO_COMPILE_ONLY:-false}" = "true" ]; then
        env_flags="-e COMPILE_ONLY=true"
        echo "  mode: compile-only"
    fi
    FRAMEC_BIN="$framec_bin" COMPILE_ONLY="${DO_COMPILE_ONLY:-false}" docker compose up --abort-on-container-exit $services 2>&1 | \
        tee /tmp/frame-test-output.txt

    echo ""
    echo "=========================================="
    echo "Summary"
    echo "=========================================="
    grep "^# " /tmp/frame-test-output.txt | sed 's/^# //' | sort
}

# Parse arguments
DO_CLEAN=false
DO_BUILD=false
DO_COMPARE=false
DO_COMPILE_ONLY=false
BUILD_FRAMEC=""
FRAMEC_BIN=""
COMPARE_A=""
COMPARE_B=""
SERVICES=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --clean) DO_CLEAN=true ;;
        --compile-only) DO_COMPILE_ONLY=true ;;
        --build) DO_BUILD=true ;;
        --build-framec)
            BUILD_FRAMEC="$2"; shift ;;
        --compare)
            DO_COMPARE=true
            COMPARE_A="$2"; COMPARE_B="$3"; shift; shift ;;
        --help|-h) usage; exit 0 ;;
        -*)
            echo "Unknown option: $1"; usage; exit 1 ;;
        *)
            if [ -z "$FRAMEC_BIN" ]; then
                FRAMEC_BIN="$1"
            else
                SERVICES="$SERVICES $1"
            fi
            ;;
    esac
    shift
done

# Build framec for Linux if requested
if [ -n "$BUILD_FRAMEC" ]; then
    build_framec_linux "$BUILD_FRAMEC"
    exit 0
fi

# Build images only
if $DO_BUILD; then
    cd "$SCRIPT_DIR"
    docker compose build
    exit 0
fi

# Compare mode
if $DO_COMPARE; then
    if [ -z "$COMPARE_A" ] || [ -z "$COMPARE_B" ]; then
        echo "Error: --compare requires two binary paths"
        exit 1
    fi
    echo "=== Running binary A: $COMPARE_A ==="
    clean_output
    run_tests "$COMPARE_A" $SERVICES 2>&1 | tee /tmp/frame-compare-a.txt
    echo ""
    echo "=== Running binary B: $COMPARE_B ==="
    clean_output
    run_tests "$COMPARE_B" $SERVICES 2>&1 | tee /tmp/frame-compare-b.txt
    echo ""
    echo "=== Diff ==="
    diff <(grep "^# " /tmp/frame-compare-a.txt | sort) \
         <(grep "^# " /tmp/frame-compare-b.txt | sort) || true
    exit 0
fi

# Normal run
if [ -z "$FRAMEC_BIN" ]; then
    echo "Error: framec binary path required"
    usage
    exit 1
fi

if $DO_CLEAN; then
    clean_output
fi

run_tests "$FRAMEC_BIN" $SERVICES
