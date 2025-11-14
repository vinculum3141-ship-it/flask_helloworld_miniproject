#!/bin/bash
set -e

# Source common utilities
source "$(dirname "$0")/lib/common.sh"

# Main execution
print_header "Kubernetes Integration Tests"
echo ""
run_pytest "test_k8s/" "-v" "Testing deployment, services, configmaps, ingress, and liveness probes"
log_success "Kubernetes tests completed!"
log_note "Note: This includes slow tests. Use 'make smoke-test' for faster feedback."
echo ""
