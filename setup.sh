#!/bin/bash

###############################################################################
# Velos AI - Automated Setup Script
# This script sets up both backend and frontend environments
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Velos AI - Production Setup Script        ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}[1/8] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.9"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo -e "${GREEN}✓ Python $PYTHON_VERSION detected (>= 3.9 required)${NC}"
else
    echo -e "${RED}✗ Python 3.9+ required. You have $PYTHON_VERSION${NC}"
    exit 1
fi

# Check Node.js
echo -e "${YELLOW}[2/8] Checking Node.js version...${NC}"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION detected${NC}"
else
    echo -e "${RED}✗ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

# Create Python virtual environment
echo -e "${YELLOW}[3/8] Creating Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    virtualenv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}[4/8] Installing Python dependencies...${NC}"
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip --quiet

# Install Python packages
pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Python packages installed${NC}"

# Download spaCy model
echo -e "${YELLOW}[5/8] Downloading spaCy language model...${NC}"
python -m spacy download en_core_web_sm --quiet
echo -e "${GREEN}✓ spaCy model downloaded${NC}"

# Create .env file if it doesn't exist
echo -e "${YELLOW}[6/8] Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created from template${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your GROQ_API_KEY${NC}"
    echo -e "${YELLOW}  Get your free API key from: https://console.groq.com${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Install frontend dependencies
echo -e "${YELLOW}[7/8] Installing frontend dependencies...${NC}"
cd velos-frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
    echo -e "${GREEN}✓ Frontend packages installed${NC}"
else
    echo -e "${GREEN}✓ Frontend packages already installed${NC}"
fi
cd ..

# Create necessary directories
echo -e "${YELLOW}[8/8] Creating application directories...${NC}"
mkdir -p chroma_db logs uploads
echo -e "${GREEN}✓ Directories created${NC}"

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            Setup Complete! 🎉                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo -e "  1. ${YELLOW}Edit .env and add your GROQ_API_KEY${NC}"
echo -e "  2. ${YELLOW}Start backend:${NC}  ./run-backend.sh"
echo -e "  3. ${YELLOW}Start frontend:${NC} ./run-frontend.sh"
echo -e "  4. ${YELLOW}Open browser:${NC}  http://localhost:5173"
echo ""
echo -e "${BLUE}For production deployment, see DEPLOYMENT.md${NC}"
echo ""
