#!/bin/bash
set -e

# Source common utilities
source "$(dirname "$0")/lib/common.sh"

# Main execution
print_header "Python Unit Tests"
echo ""
run_pytest "app/tests/" "-v" "Testing Flask application logic independently of Kubernetes"
log_success "Unit tests completed!"
echo ""
