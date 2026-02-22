#!/bin/bash
# Run all Frame V4 tests in parallel Docker containers
#
# Output: TAP format to stdout
# Usage: ./run.sh [--quiet]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QUIET="${1:-}"

cd "$SCRIPT_DIR"

if [ "$QUIET" = "--quiet" ]; then
    # Run and show only summary
    docker-compose up 2>/dev/null | grep -E "^(TAP|1\.\.|ok|not ok|#)"
else
    # Run with full output
    docker-compose up
fi
