#!/bin/bash
# Run a single Frame test in a Docker container
# Usage: ./run_docker_test.sh <language> <test_file> [additional_args]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}Usage: $0 <language> <test_file> [additional_args]${NC}"
    echo "  language: python, typescript, or rust"
    echo "  test_file: Path to the transpiled test file"
    exit 1
fi

LANGUAGE="$1"
TEST_FILE="$2"
shift 2
ADDITIONAL_ARGS="$@"

# Get absolute paths
TEST_FILE_ABS="$(cd "$(dirname "$TEST_FILE")" && pwd)/$(basename "$TEST_FILE")"
TEST_DIR="$(dirname "$TEST_FILE_ABS")"
TEST_NAME="$(basename "$TEST_FILE")"

# Determine Docker image and command based on language
case "$LANGUAGE" in
    python)
        IMAGE="frame-transpiler-python:latest"
        # Mount the test directory and run the Python file
        docker run --rm \
            -v "$TEST_DIR:/work" \
            -v "${FRAMEPILER_TEST_ENV:-$(pwd)}/framepiler/frame_runtime_py:/opt/frame_runtime_py" \
            -e PYTHONPATH=/opt:/work \
            "$IMAGE" \
            python3 "/work/$TEST_NAME" $ADDITIONAL_ARGS
        ;;
    
    typescript)
        IMAGE="frame-transpiler-typescript:latest"
        # TypeScript tests are compiled to JavaScript outside Docker
        # We just run the JavaScript file
        docker run --rm \
            -v "$TEST_DIR:/work" \
            -v "${FRAMEPILER_TEST_ENV:-$(pwd)}/framepiler/frame_runtime_ts:/opt/frame_runtime_ts" \
            -e NODE_PATH=/opt \
            "$IMAGE" \
            node "/work/$TEST_NAME" $ADDITIONAL_ARGS
        ;;
    
    rust)
        IMAGE="frame-transpiler-rust:latest"
        # For Rust, compile and run
        # The test files should be valid Rust code that can be compiled directly
        docker run --rm \
            -v "$TEST_DIR:/work" \
            "$IMAGE" \
            bash -c "cd /work && rustc $TEST_NAME -o test_binary 2>&1 && ./test_binary $ADDITIONAL_ARGS 2>&1"
        ;;
    
    *)
        echo -e "${RED}Unsupported language: $LANGUAGE${NC}"
        echo "Supported languages: python, typescript, rust"
        exit 1
        ;;
esac