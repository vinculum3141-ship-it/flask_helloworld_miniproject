#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  Kubernetes Integration Tests${NC}"
    echo -e "${BLUE}================================================${NC}"
}

run_k8s_tests() {
    echo -e "\n${GREEN}[INFO] Running Kubernetes-level tests...${NC}"
    echo -e "${YELLOW}Testing deployment, services, configmaps, ingress, and liveness probes${NC}\n"
    pytest test_k8s/ -v
}

# Run
print_header
run_k8s_tests
echo -e "\n${GREEN}✅ Kubernetes tests completed!${NC}"
echo -e "${YELLOW}Note: This includes slow tests. Use 'make smoke-test' for faster feedback.${NC}\n"
