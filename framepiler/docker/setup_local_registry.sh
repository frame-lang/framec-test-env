#!/bin/bash
# Setup local Docker registry for testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up local Docker registry...${NC}"

# Check if registry is already running
if docker ps | grep -q "local-registry"; then
    echo -e "${YELLOW}Local registry already running${NC}"
else
    # Start local registry on port 5001 (5000 often conflicts with ControlCenter on macOS)
    docker run -d \
        -p 5001:5000 \
        --restart=always \
        --name local-registry \
        registry:2
    
    echo -e "${GREEN}Local registry started on localhost:5001${NC}"
fi

# Tag images for local registry
VERSION="v0.86.71"
echo -e "${YELLOW}Tagging images for local registry...${NC}"

docker tag frame-transpiler-python:latest localhost:5001/frame-transpiler-python:latest
docker tag frame-transpiler-python:$VERSION localhost:5001/frame-transpiler-python:$VERSION

docker tag frame-transpiler-typescript:latest localhost:5001/frame-transpiler-typescript:latest
docker tag frame-transpiler-typescript:$VERSION localhost:5001/frame-transpiler-typescript:$VERSION

docker tag frame-transpiler-rust:latest localhost:5001/frame-transpiler-rust:latest
docker tag frame-transpiler-rust:$VERSION localhost:5001/frame-transpiler-rust:$VERSION

# Push to local registry
echo -e "${YELLOW}Pushing Python image...${NC}"
docker push localhost:5001/frame-transpiler-python:latest
docker push localhost:5001/frame-transpiler-python:$VERSION

echo -e "${YELLOW}Pushing TypeScript image...${NC}"
docker push localhost:5001/frame-transpiler-typescript:latest
docker push localhost:5001/frame-transpiler-typescript:$VERSION

echo -e "${YELLOW}Pushing Rust image...${NC}"
docker push localhost:5001/frame-transpiler-rust:latest
docker push localhost:5001/frame-transpiler-rust:$VERSION

echo -e "${GREEN}All images pushed to local registry!${NC}"
echo ""
echo -e "${YELLOW}Images available at:${NC}"
echo "  localhost:5001/frame-transpiler-python:$VERSION"
echo "  localhost:5001/frame-transpiler-typescript:$VERSION"
echo "  localhost:5001/frame-transpiler-rust:$VERSION"
echo ""
echo -e "${YELLOW}To test pulling:${NC}"
echo "  docker pull localhost:5001/frame-transpiler-python:latest"