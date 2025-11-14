#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  Python Unit Tests${NC}"
    echo -e "${BLUE}================================================${NC}"
}

run_unit_tests() {
    echo -e "\n${GREEN}[INFO] Running Python unit tests...${NC}"
    echo -e "${YELLOW}Testing Flask application logic independently of Kubernetes${NC}\n"
    pytest app/tests/ -v
}

# Run
print_header
run_unit_tests
echo -e "\n${GREEN}✅ Unit tests completed!${NC}\n"
