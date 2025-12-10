#!/bin/bash
# Check for Docker resource conflicts between teams
# This script helps identify potential conflicts before running tests

set -e

echo "=== Frame Test Environment Conflict Check ==="
echo "Date: $(date)"
echo ""

# Check for active containers from both teams
echo "=== Active Containers ==="
TRANSPILER_CONTAINERS=$(docker ps --format '{{.Names}}' | grep -c "frame-transpiler-" || true)
DEBUGGER_CONTAINERS=$(docker ps --format '{{.Names}}' | grep -c "frame-debugger-" || true)

echo "Transpiler containers running: $TRANSPILER_CONTAINERS"
echo "Debugger containers running: $DEBUGGER_CONTAINERS"

if [ "$TRANSPILER_CONTAINERS" -gt 0 ]; then
    echo "  Transpiler container details:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "frame-transpiler-" || true
fi

if [ "$DEBUGGER_CONTAINERS" -gt 0 ]; then
    echo "  Debugger container details:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "frame-debugger-" || true
fi

echo ""

# Check for Docker networks
echo "=== Docker Networks ==="
TRANSPILER_NETS=$(docker network ls --format '{{.Name}}' | grep -c "frame-transpiler-" || true)
DEBUGGER_NETS=$(docker network ls --format '{{.Name}}' | grep -c "frame-debugger-" || true)

echo "Transpiler networks: $TRANSPILER_NETS"
echo "Debugger networks: $DEBUGGER_NETS"

if [ "$TRANSPILER_NETS" -gt 0 ]; then
    docker network ls --format "table {{.Name}}\t{{.Driver}}" | grep "frame-transpiler-" || true
fi

if [ "$DEBUGGER_NETS" -gt 0 ]; then
    docker network ls --format "table {{.Name}}\t{{.Driver}}" | grep "frame-debugger-" || true
fi

echo ""

# Check for Docker volumes
echo "=== Docker Volumes ==="
TRANSPILER_VOLS=$(docker volume ls --format '{{.Name}}' | grep -c "frame-transpiler-" || true)
DEBUGGER_VOLS=$(docker volume ls --format '{{.Name}}' | grep -c "frame-debugger-" || true)

echo "Transpiler volumes: $TRANSPILER_VOLS"
echo "Debugger volumes: $DEBUGGER_VOLS"

echo ""

# Check resource usage
echo "=== Resource Usage ==="
if [ "$TRANSPILER_CONTAINERS" -gt 0 ] || [ "$DEBUGGER_CONTAINERS" -gt 0 ]; then
    echo "Container resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep -E "(frame-transpiler-|frame-debugger-|CONTAINER)" || true
fi

echo ""

# Check for port conflicts
echo "=== Port Usage ==="
echo "Checking for port conflicts in reserved ranges..."
echo "  Transpiler range: 9000-9499"
echo "  Debugger range: 9500-9999"

# Check if any containers are using ports
TRANSPILER_PORTS=$(docker ps --format '{{.Ports}}' --filter "name=frame-transpiler-" | grep -oE '90[0-4][0-9]' | sort -u | wc -l || true)
DEBUGGER_PORTS=$(docker ps --format '{{.Ports}}' --filter "name=frame-debugger-" | grep -oE '95[0-9][0-9]|99[0-9][0-9]' | sort -u | wc -l || true)

echo "  Transpiler ports in use: $TRANSPILER_PORTS"
echo "  Debugger ports in use: $DEBUGGER_PORTS"

echo ""

# Conflict detection
echo "=== Conflict Analysis ==="
CONFLICTS=0

# Check for namespace violations
if docker ps --format '{{.Names}}' | grep -v -E "^frame-(transpiler|debugger)-" | grep -q "^frame-"; then
    echo "❌ WARNING: Found containers with 'frame-' prefix outside namespace rules"
    CONFLICTS=$((CONFLICTS + 1))
fi

# Check for network subnet conflicts (would need more sophisticated checking)
if [ "$TRANSPILER_NETS" -gt 0 ] && [ "$DEBUGGER_NETS" -gt 0 ]; then
    echo "⚠️  Both teams have active networks - verify subnet isolation"
fi

# Check for high resource usage
TOTAL_CONTAINERS=$((TRANSPILER_CONTAINERS + DEBUGGER_CONTAINERS))
if [ "$TOTAL_CONTAINERS" -gt 30 ]; then
    echo "⚠️  WARNING: High number of containers ($TOTAL_CONTAINERS) - may impact performance"
    CONFLICTS=$((CONFLICTS + 1))
fi

if [ "$CONFLICTS" -eq 0 ]; then
    echo "✅ No conflicts detected - safe to proceed with testing"
else
    echo "❌ Found $CONFLICTS potential conflicts - review before proceeding"
fi

echo ""
echo "=== Recommendations ==="

if [ "$TRANSPILER_CONTAINERS" -gt 0 ] && [ "$DEBUGGER_CONTAINERS" -gt 0 ]; then
    echo "⚠️  Both teams have active containers. Consider:"
    echo "   - Coordinating test schedules to avoid resource contention"
    echo "   - Using the TEST_RUN_ID environment variable for unique naming"
fi

if [ "$TOTAL_CONTAINERS" -gt 20 ]; then
    echo "⚠️  Many containers running. Consider:"
    echo "   - Running cleanup: docker system prune -f"
    echo "   - Checking for stuck/orphaned containers"
fi

echo ""
echo "For team-specific cleanup:"
echo "  Transpiler: docker ps -aq --filter 'label=frame.component=transpiler' | xargs docker rm -f"
echo "  Debugger: docker ps -aq --filter 'label=frame.component=debugger' | xargs docker rm -f"

exit $CONFLICTS