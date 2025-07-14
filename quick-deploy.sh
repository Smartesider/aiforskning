#!/bin/bash
# AI Ethics Testing Framework - Quick Deploy Script
# Downloads and runs the advanced multi-server installer

set -euo pipefail

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}[DEPLOY]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're on Ubuntu/Debian
if ! command -v apt-get &> /dev/null; then
    print_error "This installer requires Ubuntu/Debian with apt-get"
    exit 1
fi

print_header "AI Ethics Testing Framework - Quick Deploy"
echo ""

# Get the repository URL
REPO_URL="https://github.com/Smartesider/aiforskning.git"
TEMP_DIR="/tmp/aiforskning-deploy-$$"

print_header "Downloading latest code from GitHub..."

# Install git if not available
if ! command -v git &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y git
fi

# Clone the repository
git clone "$REPO_URL" "$TEMP_DIR"
cd "$TEMP_DIR"

print_success "Repository downloaded successfully"

# Make installer executable
chmod +x install-advanced.sh

print_header "Starting advanced installer..."
echo ""
echo "The advanced installer will now start with intelligent conflict detection,"
echo "SSL automation, and multi-server support."
echo ""

# Run the advanced installer with all arguments passed through
./install-advanced.sh "$@"

# Cleanup
cd /
rm -rf "$TEMP_DIR"

print_success "Deployment completed!"
