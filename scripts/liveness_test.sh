#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  Liveness Probe Configuration Tests${NC}"
    echo -e "${BLUE}================================================${NC}"
}

run_automated_tests() {
    echo -e "\n${GREEN}[INFO] Running automated liveness probe configuration tests...${NC}"
    echo -e "${YELLOW}(Behavioral tests available in test_crash_recovery_manual.py)${NC}\n"
    pytest test_k8s/test_liveness_probe.py -v -s
}

run_manual_tests() {
    echo -e "\n${GREEN}[INFO] Running manual self-healing tests...${NC}"
    echo -e "${YELLOW}(These tests involve timing and may take 60-90 seconds)${NC}\n"
    pytest test_k8s/ -v -s -m manual
}

run_config_only() {
    echo -e "\n${GREEN}[INFO] Running liveness probe configuration check only...${NC}\n"
    pytest test_k8s/test_liveness_probe.py::test_liveness_probe_configured -v -s
}

show_help() {
    echo "Usage: bash scripts/liveness_test.sh [OPTION]"
    echo ""
    echo "Options:"
    echo "  (no option)  Run automated configuration tests (default, fast)"
    echo "  --manual     Run manual behavioral/timing tests (pod deletion, crash recovery)"
    echo "  --config     Run only the liveness probe configuration check"
    echo "  --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  bash scripts/liveness_test.sh           # Automated config tests"
    echo "  bash scripts/liveness_test.sh --manual  # Manual behavioral tests"
    echo "  bash scripts/liveness_test.sh --config  # Configuration check only"
}

# Main script logic
print_header

case "${1:-}" in
    --manual)
        run_manual_tests
        ;;
    --config)
        run_config_only
        ;;
    --help|-h)
        show_help
        ;;
    "")
        run_automated_tests
        ;;
    *)
        echo -e "${YELLOW}[WARNING] Unknown option: $1${NC}"
        show_help
        exit 1
        ;;
esac

echo -e "\n${GREEN}✅ Tests completed!${NC}\n"
