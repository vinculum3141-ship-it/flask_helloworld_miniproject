#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Running Smoke Tests${NC}"
echo -e "${BLUE}================================================${NC}"

echo -e "\n${GREEN}[INFO] Running smoke tests to verify deployment...${NC}"
echo -e "${YELLOW}This includes: deployment, configmap, service access, and liveness probe configuration${NC}\n"

# Run all K8s tests (now all are fast configuration checks)
# Timing-dependent behavioral tests have been moved to manual suite
pytest test_k8s/ -v

echo -e "\n${GREEN}✅ Smoke tests completed successfully!${NC}"
echo -e "${YELLOW}Note: Behavioral/timing tests (pod deletion, crash recovery) are in test_crash_recovery_manual.py${NC}"
echo -e "${YELLOW}To run manual tests: pytest test_k8s/test_crash_recovery_manual.py -v -s${NC}\n"