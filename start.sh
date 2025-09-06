#!/bin/bash

# AI Storybook Generator - Start Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Set base directory
BASE_DIR=$(pwd)
BACKEND_DIR="${BASE_DIR}/backend"
FRONTEND_DIR="${BASE_DIR}/frontend"
LOG_DIR="${BASE_DIR}/logs"
BACKEND_LOG="${LOG_DIR}/backend.log"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to show banner
show_banner() {
    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     🎨 AI Storybook Generator 📚         ║${NC}"
    echo -e "${BLUE}║        Powered by Gemini Flash           ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to check if a service is running
is_service_running() {
    local pattern=$1
    if pgrep -f "$pattern" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to check port availability
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port is in use${NC}"
        
        # Check if it's AirPlay Receiver (macOS specific)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            if lsof -i :$port | grep -q "ControlCe"; then
                echo -e "${YELLOW}   It appears to be macOS AirPlay Receiver${NC}"
                echo -e "${YELLOW}   To disable: System Settings → General → AirDrop & Handoff → AirPlay Receiver${NC}"
            fi
        fi
        
        echo -e "${RED}   Would you like to:${NC}"
        echo "   1) Kill the process using port $port"
        echo "   2) Use a different port"
        echo "   3) Exit"
        read -p "   Choose (1/2/3): " choice
        
        case $choice in
            1)
                echo "   Attempting to kill process on port $port..."
                lsof -ti:$port | xargs kill -9 2>/dev/null
                sleep 2
                if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                    echo -e "${RED}   Failed to kill process. May require sudo.${NC}"
                    return 1
                else
                    echo -e "${GREEN}   Port $port is now free.${NC}"
                    return 0
                fi
                ;;
            2)
                read -p "   Enter new port for $service: " new_port
                export BACKEND_PORT=$new_port
                echo -e "${GREEN}   Using port $new_port for $service${NC}"
                return 0
                ;;
            *)
                echo -e "${RED}   Exiting...${NC}"
                exit 1
                ;;
        esac
    else
        return 0
    fi
}

# Function to install dependencies
install_dependencies() {
    echo -e "${YELLOW}📦 Checking Python dependencies...${NC}"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    pip install -q -r requirements.txt 2>/dev/null
    
    # Check specific packages
    python -c "import flask" 2>/dev/null || pip install flask
    python -c "import flask_cors" 2>/dev/null || pip install flask-cors
    python -c "import google.generativeai" 2>/dev/null || pip install google-generativeai
    python -c "import reportlab" 2>/dev/null || pip install reportlab
    python -c "import psutil" 2>/dev/null || pip install psutil
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Function to start backend
start_backend() {
    local port=${BACKEND_PORT:-5000}
    
    if is_service_running "flask.*app.py"; then
        echo -e "${YELLOW}⚠️  Backend is already running${NC}"
        local pid=$(pgrep -f "flask.*app.py")
        echo "   PID: $pid"
    else
        echo -e "${BLUE}🚀 Starting backend server on port $port...${NC}"
        
        # Backup and clear old log
        if [ -f "$BACKEND_LOG" ]; then
            mv "$BACKEND_LOG" "${BACKEND_LOG}.$(date +%Y%m%d_%H%M%S).bak" 2>/dev/null
        fi
        
        # Start backend
        cd "$BACKEND_DIR"
        BACKEND_PORT=$port python app.py > "$BACKEND_LOG" 2>&1 &
        local pid=$!
        
        # Wait for backend to start
        sleep 3
        
        if ps -p $pid > /dev/null; then
            echo -e "${GREEN}✅ Backend started successfully${NC}"
            echo "   PID: $pid"
            echo "   URL: http://localhost:$port"
            echo "   Logs: $BACKEND_LOG"
        else
            echo -e "${RED}❌ Failed to start backend${NC}"
            echo "   Check logs: $BACKEND_LOG"
            tail -10 "$BACKEND_LOG"
            return 1
        fi
        
        cd "$BASE_DIR"
    fi
}

# Function to open frontend
open_frontend() {
    echo -e "${BLUE}🌐 Opening frontend...${NC}"
    
    local frontend_file="${FRONTEND_DIR}/index.html"
    
    if [ ! -f "$frontend_file" ]; then
        echo -e "${RED}❌ Frontend file not found: $frontend_file${NC}"
        return 1
    fi
    
    # Update API URL in config if port changed
    if [ ! -z "$BACKEND_PORT" ] && [ "$BACKEND_PORT" != "5000" ]; then
        echo "   Updating frontend config for port $BACKEND_PORT..."
        sed -i.bak "s|http://localhost:5000|http://localhost:$BACKEND_PORT|g" "${FRONTEND_DIR}/js/config.js" 2>/dev/null
    fi
    
    # Open in browser based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "file://${frontend_file}"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "file://${frontend_file}" 2>/dev/null || firefox "file://${frontend_file}" 2>/dev/null
    else
        echo "   Please open in browser: file://${frontend_file}"
    fi
    
    echo -e "${GREEN}✅ Frontend opened in browser${NC}"
}

# Main execution
main() {
    show_banner
    
    # Check .env file
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo -e "${YELLOW}   Please update .env with your API keys${NC}"
            exit 1
        fi
    fi
    
    # Load environment variables
    export $(grep -v '^#' .env | xargs)
    
    # Check API key
    if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" == "your_gemini_api_key_here" ]; then
        echo -e "${RED}❌ Please set your GEMINI_API_KEY in .env file${NC}"
        echo "   Get your API key from: https://makersuite.google.com/app/apikey"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Configuration loaded${NC}"
    echo ""
    
    # Check port availability
    check_port ${BACKEND_PORT:-5000} "Backend"
    
    # Install dependencies
    install_dependencies
    
    echo ""
    
    # Start backend
    start_backend
    
    if [ $? -eq 0 ]; then
        echo ""
        
        # Open frontend
        open_frontend
        
        echo ""
        echo -e "${GREEN}════════════════════════════════════════════${NC}"
        echo -e "${GREEN}✨ AI Storybook Generator is running!${NC}"
        echo -e "${GREEN}════════════════════════════════════════════${NC}"
        echo ""
        echo "Backend:  http://localhost:${BACKEND_PORT:-5000}"
        echo "Frontend: Open in your browser"
        echo "API Docs: http://localhost:${BACKEND_PORT:-5000}/api"
        echo ""
        echo "Commands:"
        echo "  📊 Check status:  ./status.sh"
        echo "  🛑 Stop services: ./stop.sh"
        echo "  📝 View logs:     tail -f logs/backend.log"
        echo ""
        echo "Press Ctrl+C to stop watching (services will continue running)"
    else
        echo -e "${RED}❌ Failed to start services${NC}"
        exit 1
    fi
}

# Run main function
main