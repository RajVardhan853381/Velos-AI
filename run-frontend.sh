#!/bin/bash

###############################################################################
# Velos AI - Frontend Development Server Startup Script
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Velos AI Frontend...${NC}"

# Check if node_modules exists
if [ ! -d "velos-frontend/node_modules" ]; then
    echo -e "${YELLOW}Frontend dependencies not found. Running setup...${NC}"
    ./setup.sh
fi

# Navigate to frontend directory
cd velos-frontend

# Start the development server
echo -e "${GREEN}Starting Vite dev server on http://localhost:5173${NC}"
npm run dev
