#!/bin/bash
set -e

# Source common utilities
source "$(dirname "$0")/lib/common.sh"

# Main execution
print_header "Kubernetes Integration Tests"
echo ""
run_pytest "test_k8s/" "-v -m 'not manual'" "Testing deployment, services, configmaps, ingress, and liveness probes"
log_success "Kubernetes tests completed!"
log_note "Note: Manual/timing-dependent tests excluded. Run with 'pytest test_k8s/ -v -m manual' for manual tests."
echo ""
