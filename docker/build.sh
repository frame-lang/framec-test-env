#!/bin/bash
# Build Docker images for Frame V4 test runners
#
# Usage: ./build.sh [--local]
#
# By default, builds framec for Linux inside Docker.
# Use --local to skip building framec (assumes it's already in docker/*/framec)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TRANSPILER_DIR="/Users/marktruluck/projects/frame_transpiler"

if [ "$1" != "--local" ]; then
    echo "Building framec for Linux..."

    # Build framec in a Linux container
    # Copy source to container (can't build in read-only mount)
    docker run --rm \
        -v "$TRANSPILER_DIR:/src:ro" \
        -v "$SCRIPT_DIR:/out" \
        rust:1.83-slim \
        bash -c "cp -r /src /build && cd /build && cargo build --release -p framec && cp target/release/framec /out/framec-linux"

    # Copy to each language directory
    for lang in python typescript rust; do
        cp "$SCRIPT_DIR/framec-linux" "$SCRIPT_DIR/$lang/framec"
    done

    echo "framec built for Linux"
fi

echo "Building Docker images..."

# Build images
cd "$SCRIPT_DIR"
docker-compose build

echo ""
echo "Build complete. Run tests with:"
echo "  cd $SCRIPT_DIR && docker-compose up"
