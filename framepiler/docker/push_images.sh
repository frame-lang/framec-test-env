#!/bin/bash
# Push Docker images to GitHub Container Registry

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Registry configuration
REGISTRY="ghcr.io/frame-lang"
VERSION="v0.86.71"

echo -e "${GREEN}Pushing Docker images to GitHub Container Registry...${NC}"

# Check if logged in to ghcr.io
if ! docker info 2>/dev/null | grep -q "ghcr.io"; then
    echo -e "${YELLOW}Please login to GitHub Container Registry first:${NC}"
    echo "  echo \$GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin"
    exit 1
fi

# Tag images for registry
echo -e "${YELLOW}Tagging images for registry...${NC}"

docker tag frame-transpiler-python:latest $REGISTRY/frame-transpiler-python:latest
docker tag frame-transpiler-python:$VERSION $REGISTRY/frame-transpiler-python:$VERSION

docker tag frame-transpiler-typescript:latest $REGISTRY/frame-transpiler-typescript:latest
docker tag frame-transpiler-typescript:$VERSION $REGISTRY/frame-transpiler-typescript:$VERSION

docker tag frame-transpiler-rust:latest $REGISTRY/frame-transpiler-rust:latest
docker tag frame-transpiler-rust:$VERSION $REGISTRY/frame-transpiler-rust:$VERSION

# Push Python image
echo -e "${YELLOW}Pushing Python image...${NC}"
docker push $REGISTRY/frame-transpiler-python:latest
docker push $REGISTRY/frame-transpiler-python:$VERSION

# Push TypeScript image
echo -e "${YELLOW}Pushing TypeScript image...${NC}"
docker push $REGISTRY/frame-transpiler-typescript:latest
docker push $REGISTRY/frame-transpiler-typescript:$VERSION

# Push Rust image
echo -e "${YELLOW}Pushing Rust image...${NC}"
docker push $REGISTRY/frame-transpiler-rust:latest
docker push $REGISTRY/frame-transpiler-rust:$VERSION

echo -e "${GREEN}All images successfully pushed to registry!${NC}"
echo ""
echo -e "${YELLOW}Images available at:${NC}"
echo "  $REGISTRY/frame-transpiler-python:$VERSION"
echo "  $REGISTRY/frame-transpiler-typescript:$VERSION"
echo "  $REGISTRY/frame-transpiler-rust:$VERSION"