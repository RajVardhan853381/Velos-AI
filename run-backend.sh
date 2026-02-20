#!/bin/bash

###############################################################################
# Velos AI - Backend Server Startup Script
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Velos AI Backend Server...${NC}"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Running setup...${NC}"
    ./setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo -e "${YELLOW}Please run setup.sh first and configure your GROQ_API_KEY${NC}"
    exit 1
fi

# Start the server
echo -e "${GREEN}Starting FastAPI server on http://localhost:8000${NC}"
uvicorn server:app --reload --host 0.0.0.0 --port 8000
