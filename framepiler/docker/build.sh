#!/bin/bash
# Build the Rust Docker test runner

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building Frame Docker Runner..."
cargo build --release

if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "Binary location: $SCRIPT_DIR/target/release/frame-docker-runner"
    
    # Make it executable
    chmod +x target/release/frame-docker-runner
    
    echo ""
    echo "Usage:"
    echo "  ./target/release/frame-docker-runner <language> <category> --framec <path>"
    echo ""
    echo "Example:"
    echo "  ./target/release/frame-docker-runner python v3_data_types --framec ../../../target/release/framec"
else
    echo "Build failed!"
    exit 1
fi