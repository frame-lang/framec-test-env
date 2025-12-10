#!/bin/bash
# Build Docker images for Frame Transpiler PRT language testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Docker images for Frame Transpiler testing...${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Image tag version
VERSION="v0.86.71"
REGISTRY="ghcr.io/frame-transpiler"

# Build Python image
echo -e "${YELLOW}Building Python test image...${NC}"
docker build -f "$SCRIPT_DIR/Dockerfile.python" \
    -t frame-transpiler-python:latest \
    -t frame-transpiler-python:$VERSION \
    -t $REGISTRY/frame-transpiler-python:latest \
    -t $REGISTRY/frame-transpiler-python:$VERSION \
    "$SCRIPT_DIR"

# Build TypeScript image
echo -e "${YELLOW}Building TypeScript test image...${NC}"
docker build -f "$SCRIPT_DIR/Dockerfile.typescript" \
    -t frame-transpiler-typescript:latest \
    -t frame-transpiler-typescript:$VERSION \
    -t $REGISTRY/frame-transpiler-typescript:latest \
    -t $REGISTRY/frame-transpiler-typescript:$VERSION \
    "$SCRIPT_DIR"

# Build Rust image
echo -e "${YELLOW}Building Rust test image...${NC}"
docker build -f "$SCRIPT_DIR/Dockerfile.rust" \
    -t frame-transpiler-rust:latest \
    -t frame-transpiler-rust:$VERSION \
    -t $REGISTRY/frame-transpiler-rust:latest \
    -t $REGISTRY/frame-transpiler-rust:$VERSION \
    "$SCRIPT_DIR"

echo -e "${GREEN}All Docker images built successfully!${NC}"

# List built images
echo -e "${YELLOW}Built images:${NC}"
docker images | grep frame-transpiler | head -10

echo -e "${GREEN}To push images to registry, run:${NC}"
echo "docker push $REGISTRY/frame-transpiler-python:$VERSION"
echo "docker push $REGISTRY/frame-transpiler-typescript:$VERSION"
echo "docker push $REGISTRY/frame-transpiler-rust:$VERSION"