#!/bin/bash
# Wrapper script to run Docker tests using the Rust runner

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
FRAMEC_PATH="${FRAMEC_PATH:-../../../target/release/framec}"
SHARED_ENV="${FRAMEPILER_TEST_ENV:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

# Parse arguments
if [ $# -lt 2 ]; then
    echo -e "${RED}Usage: $0 <language> <category> [options]${NC}"
    echo "  language: python, typescript, or rust"
    echo "  category: v3_data_types, v3_operators, v3_scoping, v3_systems, etc."
    echo ""
    echo "Options:"
    echo "  --framec PATH    Path to framec binary (default: $FRAMEC_PATH)"
    echo "  --json           Output results as JSON"
    echo "  -v, --verbose    Verbose output"
    exit 1
fi

LANGUAGE="$1"
CATEGORY="$2"
shift 2

# Map language names
case "$LANGUAGE" in
    python)
        LANG="python_3"
        ;;
    typescript|ts)
        LANG="typescript"
        ;;
    rust|rs)
        LANG="rust"
        ;;
    *)
        LANG="$LANGUAGE"
        ;;
esac

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="$SCRIPT_DIR/target/release/frame-docker-runner"

# Check if runner is built
if [ ! -f "$RUNNER" ]; then
    echo -e "${YELLOW}Rust Docker runner not built. Building now...${NC}"
    "$SCRIPT_DIR/build.sh"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to build Rust Docker runner${NC}"
        exit 1
    fi
fi

# Run tests
echo -e "${GREEN}Running $LANG tests for $CATEGORY...${NC}"
"$RUNNER" "$LANG" "$CATEGORY" --framec "$FRAMEC_PATH" --shared-env "$SHARED_ENV" "$@"