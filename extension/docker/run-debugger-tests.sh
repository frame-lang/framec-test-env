#!/bin/bash

# Frame VS Code Extension Debugger Test Runner
# Follows segregation policy for frame-debugger-* namespace

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.debugger-test.yml"
NAMESPACE="frame-debugger"
TEAM="extension"
DEFAULT_TIMEOUT=300
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
export TIMESTAMP

# Function to print colored output
print_color() {
    color=$1
    message=$2
    echo -e "${color}[${NAMESPACE}] ${message}${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
Frame VS Code Extension Debugger Test Runner

Usage: $0 [COMMAND] [OPTIONS]

Commands:
    all         Run all tests (default)
    unit        Run unit tests only
    integration Run integration tests
    smoke       Run smoke tests
    debug       Start container in debug mode
    watch       Start in watch mode for development
    shell       Open a shell in the test container
    build       Build the Docker image only
    clean       Clean up debugger containers and volumes
    status      Show debugger container status
    logs        Show test logs
    help        Show this help message

Options:
    --no-cache  Build without Docker cache
    --timeout   Set test timeout in seconds (default: $DEFAULT_TIMEOUT)
    --verbose   Show verbose output
    --keep      Keep container running after tests

Environment Variables:
    FRAME_TEST_NAMESPACE    Set to 'debugger' (automatic)
    FRAME_TEST_COMPONENT    Component being tested
    TEST_RUN_ID            Unique test run identifier

Examples:
    $0                  # Run all tests
    $0 unit            # Run unit tests only
    $0 debug           # Start in debug mode
    $0 build --no-cache # Rebuild image from scratch
    $0 status          # Check container status

EOF
}

# Function to check for conflicts with transpiler team
check_conflicts() {
    print_color "$YELLOW" "Checking for namespace conflicts..."
    
    # Check for transpiler containers
    if docker ps -a --format "{{.Names}}" | grep -q "frame-transpiler-"; then
        print_color "$YELLOW" "⚠ Transpiler team containers detected (no conflict, different namespace)"
        docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep "frame-transpiler-" || true
    fi
    
    # Check our containers
    if docker ps -a --format "{{.Names}}" | grep -q "${NAMESPACE}-"; then
        print_color "$BLUE" "Existing debugger containers found:"
        docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep "${NAMESPACE}-"
    fi
    
    # Check networks
    local our_nets=$(docker network ls --format "{{.Name}}" | grep "${NAMESPACE}-" || true)
    if [ -n "$our_nets" ]; then
        print_color "$BLUE" "Debugger networks: $our_nets"
    fi
}

# Function to check Docker and Docker Compose
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_color "$RED" "Docker is not installed or not running"
        exit 1
    fi
    
    # Check for docker compose (v2) or docker-compose (v1)
    if docker compose version &> /dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        print_color "$RED" "Docker Compose is not installed"
        exit 1
    fi
    
    print_color "$GREEN" "✓ Docker and Docker Compose are available"
}

# Function to build Docker image
build_image() {
    print_color "$YELLOW" "Building debugger test image..."
    
    # Ensure we're in the right directory
    cd "$(dirname "$0")"
    
    $DOCKER_COMPOSE -f $COMPOSE_FILE build $NO_CACHE frame-debugger-test
    
    print_color "$GREEN" "✓ Debugger test image built successfully"
    
    # Tag the image for easy reference
    docker tag frame-debugger/test-base:latest ${NAMESPACE}/test:${TIMESTAMP}
}

# Function to run tests
run_tests() {
    local profile=$1
    local service=$2
    
    print_color "$YELLOW" "Running $profile tests in debugger namespace..."
    print_color "$BLUE" "Test Run ID: debugger-${TIMESTAMP}-$$"
    
    # Set environment
    export TEST_TIMEOUT=$TIMEOUT
    export TEST_RUN_ID="debugger-${TIMESTAMP}-$$"
    export FRAME_TEST_NAMESPACE="debugger"
    
    cd "$(dirname "$0")"
    
    if [ -z "$profile" ] || [ "$profile" == "all" ]; then
        # Run default service
        $DOCKER_COMPOSE -f $COMPOSE_FILE up --abort-on-container-exit --exit-code-from frame-debugger-test frame-debugger-test
    else
        # Run specific profile
        $DOCKER_COMPOSE -f $COMPOSE_FILE --profile $profile up --abort-on-container-exit --exit-code-from ${service} ${service}
    fi
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_color "$GREEN" "✓ Tests passed successfully"
    else
        print_color "$RED" "✗ Tests failed with exit code $exit_code"
        
        # Save logs to results
        mkdir -p ../results/${TEST_RUN_ID}
        $DOCKER_COMPOSE -f $COMPOSE_FILE logs > ../results/${TEST_RUN_ID}/docker.log 2>&1
        print_color "$YELLOW" "Logs saved to: extension/results/${TEST_RUN_ID}/docker.log"
        
        exit $exit_code
    fi
}

# Function to clean up debugger resources only
cleanup() {
    print_color "$YELLOW" "Cleaning up debugger containers and volumes..."
    
    cd "$(dirname "$0")"
    
    # Stop and remove containers with our namespace
    $DOCKER_COMPOSE -f $COMPOSE_FILE down -v
    
    # Clean up any orphaned debugger containers
    docker ps -a --filter "label=frame.component=debugger" -q | xargs -r docker rm -f
    
    # Clean up debugger networks
    docker network ls --filter "label=frame.component=debugger" -q | xargs -r docker network rm
    
    # Clean up debugger volumes
    docker volume ls --filter "label=frame.component=debugger" -q | xargs -r docker volume rm
    
    print_color "$GREEN" "✓ Debugger cleanup complete (transpiler resources untouched)"
}

# Function to show status
show_status() {
    print_color "$BLUE" "Debugger Test Environment Status"
    echo "================================="
    
    print_color "$YELLOW" "Containers:"
    docker ps -a --filter "label=frame.component=debugger" \
        --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    print_color "$YELLOW" "\nNetworks:"
    docker network ls --filter "label=frame.component=debugger" \
        --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"
    
    print_color "$YELLOW" "\nVolumes:"
    docker volume ls --filter "label=frame.component=debugger" \
        --format "table {{.Name}}\t{{.Driver}}"
    
    print_color "$YELLOW" "\nResource Usage:"
    docker stats --no-stream --filter "label=frame.component=debugger" \
        --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" || true
}

# Function to show logs
show_logs() {
    cd "$(dirname "$0")"
    $DOCKER_COMPOSE -f $COMPOSE_FILE logs -f
}

# Function to open shell
open_shell() {
    print_color "$YELLOW" "Opening shell in debugger test container..."
    cd "$(dirname "$0")"
    $DOCKER_COMPOSE -f $COMPOSE_FILE run --rm frame-debugger-test bash
}

# Parse command
COMMAND=${1:-all}
shift || true

# Parse options
NO_CACHE=""
TIMEOUT=$DEFAULT_TIMEOUT
VERBOSE=""
KEEP=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE="-v"
            set -x
            shift
            ;;
        --keep)
            KEEP="1"
            shift
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            print_color "$RED" "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
print_color "$BLUE" "Frame Debugger Test Runner v1.0"
print_color "$BLUE" "Namespace: ${NAMESPACE}"
print_color "$BLUE" "Team: ${TEAM}"
echo ""

check_docker
check_conflicts

case $COMMAND in
    all)
        build_image
        run_tests "all" "frame-debugger-test"
        ;;
    unit)
        build_image
        run_tests "unit" "frame-debugger-unit-test"
        ;;
    integration)
        build_image
        run_tests "integration" "frame-debugger-integration-test"
        ;;
    smoke)
        build_image
        run_tests "smoke" "frame-debugger-smoke-test"
        ;;
    debug)
        build_image
        print_color "$YELLOW" "Starting container in debug mode..."
        print_color "$YELLOW" "Ports:"
        print_color "$YELLOW" "  - Debug: localhost:9501"
        print_color "$YELLOW" "  - Node debugger: localhost:9510"
        print_color "$YELLOW" "  - Python debugger: localhost:9511"
        cd "$(dirname "$0")"
        $DOCKER_COMPOSE -f $COMPOSE_FILE --profile debug up frame-debugger-test-debug
        ;;
    watch)
        build_image
        print_color "$YELLOW" "Starting in watch mode..."
        cd "$(dirname "$0")"
        $DOCKER_COMPOSE -f $COMPOSE_FILE --profile watch up frame-debugger-test-watch
        ;;
    build)
        build_image
        ;;
    clean)
        cleanup
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    shell)
        build_image
        open_shell
        ;;
    help|--help|-h)
        show_usage
        exit 0
        ;;
    *)
        print_color "$RED" "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac

print_color "$GREEN" "Done!"