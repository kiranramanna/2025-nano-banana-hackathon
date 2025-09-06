#!/bin/bash

# AI Storybook Generator - Status Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to check service status
check_service() {
    local service_name=$1
    local service_pattern=$2
    local default_port=$3
    
    echo -e "${BLUE}▶ $service_name${NC}"
    
    # Check if the service is running
    local service_pids=$(pgrep -f "$service_pattern" 2>/dev/null)
    
    if [ -n "$service_pids" ]; then
        echo -e "  ${GREEN}✅ Status: RUNNING${NC}"
        
        for pid in $service_pids; do
            # Get process details
            local process_info=$(ps -p $pid -o comm=,args= 2>/dev/null | head -1)
            echo "  PID: $pid"
            
            # Try to find listening ports for this PID
            local ports=$(lsof -Pan -p $pid -i 2>/dev/null | grep LISTEN | awk '{print $9}' | sed 's/.*://' | sort -u)
            
            if [ -n "$ports" ]; then
                for port in $ports; do
                    echo -e "  ${CYAN}Port: $port${NC}"
                    echo "  URL: http://localhost:$port"
                done
            fi
        done
        
        # Check process memory and CPU
        if command -v ps >/dev/null 2>&1; then
            local stats=$(ps -p $service_pids -o %cpu=,%mem= 2>/dev/null | tail -1)
            if [ -n "$stats" ]; then
                echo "  Resources: CPU $(echo $stats | awk '{print $1}')%, MEM $(echo $stats | awk '{print $2}')%"
            fi
        fi
    else
        echo -e "  ${RED}❌ Status: NOT RUNNING${NC}"
        
        # Check if port is in use by something else
        if [ -n "$default_port" ]; then
            local port_user=$(lsof -i :$default_port 2>/dev/null | grep LISTEN | head -1)
            if [ -n "$port_user" ]; then
                echo -e "  ${YELLOW}⚠️  Port $default_port is in use by another process${NC}"
            else
                echo -e "  ${GREEN}✅ Port $default_port is available${NC}"
            fi
        fi
    fi
    echo ""
}

# Function to check port status
check_port_detailed() {
    local port=$1
    local service_name=$2
    
    local port_info=$(lsof -i :$port 2>/dev/null | grep LISTEN)
    
    if [ -n "$port_info" ]; then
        local pid=$(echo "$port_info" | awk '{print $2}')
        local process=$(echo "$port_info" | awk '{print $1}')
        echo -e "${CYAN}Port $port ($service_name):${NC} In use by $process (PID: $pid)"
    else
        echo -e "${CYAN}Port $port ($service_name):${NC} ${GREEN}Available${NC}"
    fi
}

# Function to check API health
check_api_health() {
    local port=$1
    local endpoint="http://localhost:$port/api/health"
    
    if command -v curl >/dev/null 2>&1; then
        local response=$(curl -s -o /dev/null -w "%{http_code}" $endpoint 2>/dev/null)
        if [ "$response" = "200" ]; then
            echo -e "  ${GREEN}✅ API Health: OK${NC}"
            
            # Get detailed health info
            local health_data=$(curl -s $endpoint 2>/dev/null)
            if [ -n "$health_data" ]; then
                echo "  API Response: $health_data" | head -1
            fi
        else
            echo -e "  ${YELLOW}⚠️  API Health: Not responding (HTTP $response)${NC}"
        fi
    fi
}

# Show banner
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   📊 AI Storybook Generator Status       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs) 2>/dev/null
    echo -e "${GREEN}✅ Configuration loaded from .env${NC}"
else
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
fi

BACKEND_PORT=${BACKEND_PORT:-5000}

echo ""
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  SERVICE STATUS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""

# Check Backend Service
check_service "Backend (Flask)" "app.py" $BACKEND_PORT

# Check API Health
if pgrep -f "app.py" > /dev/null 2>&1; then
    check_api_health $BACKEND_PORT
fi

echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  PORT STATUS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""

check_port_detailed $BACKEND_PORT "Backend API"

echo ""
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  SYSTEM RESOURCES${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""

# Check Python version
echo -e "${BLUE}Python Version:${NC}"
python3 --version

echo ""

# Check disk usage for project
echo -e "${BLUE}Project Disk Usage:${NC}"
du -sh . 2>/dev/null || echo "Unable to calculate"

echo ""

# Check log files
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  LOG FILES${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""

if [ -d "logs" ]; then
    echo -e "${BLUE}Recent logs:${NC}"
    ls -lah logs/ 2>/dev/null | tail -5
    
    # Show last few lines of backend log if it exists
    if [ -f "logs/backend.log" ]; then
        echo ""
        echo -e "${BLUE}Last 5 lines of backend.log:${NC}"
        tail -5 logs/backend.log
    fi
else
    echo "No logs directory found"
fi

echo ""
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  QUICK COMMANDS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""

if pgrep -f "app.py" > /dev/null 2>&1; then
    echo "🛑 Stop services:  ./stop.sh"
    echo "📝 View logs:      tail -f logs/backend.log"
    echo "🔄 Restart:        ./stop.sh && ./start.sh"
else
    echo "🚀 Start services: ./start.sh"
fi

echo ""
echo "🌐 Frontend URL:   file://$(pwd)/frontend/index.html"
echo "🔧 Backend API:    http://localhost:$BACKEND_PORT"
echo "📚 API Health:     http://localhost:$BACKEND_PORT/api/health"

echo ""
echo -e "${GREEN}Status check complete.${NC}"
echo ""