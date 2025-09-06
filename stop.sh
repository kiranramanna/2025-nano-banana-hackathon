#!/bin/bash

# AI Storybook Generator - Stop Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to kill a process by pattern
kill_process() {
    local pattern=$1
    local service_name=$2
    
    # Check if the process is running
    if ! pgrep -f "$pattern" > /dev/null 2>&1; then
        echo -e "${YELLOW}$service_name is not running.${NC}"
        return 0
    fi
    
    echo -e "${BLUE}Stopping $service_name...${NC}"
    
    # Get PIDs
    local pids=$(pgrep -f "$pattern")
    echo "  Found PIDs: $pids"
    
    # First try graceful kill
    pkill -f "$pattern"
    
    # Wait for 3 seconds
    sleep 3
    
    # Check if still running and force kill if necessary
    while pgrep -f "$pattern" > /dev/null 2>&1; do
        echo -e "${YELLOW}  $service_name is still running. Force killing...${NC}"
        pkill -9 -f "$pattern"
        sleep 2
    done
    
    echo -e "${GREEN}✅ $service_name has been stopped.${NC}"
}

# Function to kill process on port
kill_port() {
    local port=$1
    local service_name=$2
    
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [ -z "$pids" ]; then
        echo -e "${YELLOW}No process found on port $port${NC}"
        return 0
    fi
    
    echo -e "${BLUE}Killing process on port $port ($service_name)...${NC}"
    echo "  PIDs: $pids"
    
    # Kill the processes
    echo "$pids" | xargs kill -9 2>/dev/null
    
    sleep 1
    
    # Verify
    if lsof -ti:$port 2>/dev/null; then
        echo -e "${RED}  Failed to kill process on port $port${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $port is now free${NC}"
        return 0
    fi
}

# Show banner
echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}   🛑 Stopping AI Storybook Generator${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# Load environment variables to get ports
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs) 2>/dev/null
fi

BACKEND_PORT=${BACKEND_PORT:-5000}

# Stop Flask backend
echo -e "${BLUE}▶ Stopping Backend Services${NC}"
kill_process "flask.*app.py" "Flask Backend"
kill_process "python.*app.py" "Python Backend"
kill_process "app.py.*--port.*$BACKEND_PORT" "Backend on port $BACKEND_PORT"

# Also try to kill by port
echo ""
echo -e "${BLUE}▶ Checking ports${NC}"
kill_port $BACKEND_PORT "Backend"

# Clean up any stray Python processes related to our app
echo ""
echo -e "${BLUE}▶ Cleaning up stray processes${NC}"
kill_process "python.*backend/app" "Backend App"
kill_process "python.*run.py" "Run Script"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ All AI Storybook services have been stopped${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"

# Show remaining related processes (for verification)
echo ""
echo -e "${BLUE}▶ Verification (remaining processes):${NC}"
remaining=$(pgrep -fl python | grep -E "(app\.py|flask|backend)" 2>/dev/null)
if [ -z "$remaining" ]; then
    echo -e "${GREEN}  No related Python processes found.${NC}"
else
    echo -e "${YELLOW}  Remaining processes:${NC}"
    echo "$remaining"
fi

# Check if port is free
echo ""
echo -e "${BLUE}▶ Port status:${NC}"
if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}  ⚠️  Port $BACKEND_PORT is still in use${NC}"
    lsof -i :$BACKEND_PORT
else
    echo -e "${GREEN}  ✅ Port $BACKEND_PORT is free${NC}"
fi

echo ""