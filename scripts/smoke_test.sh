#!/bin/bash
set -e

# Source common utilities
source "$(dirname "$0")/lib/common.sh"

# Main execution
print_header "Running Smoke Tests"
echo ""
log_info "Running smoke tests to verify deployment..."
log_note "This includes: deployment, configmap, service access, and liveness probe configuration"
echo ""

# Run all K8s tests (now all are fast configuration checks)
# Timing-dependent behavioral tests have been moved to manual suite
run_pytest "test_k8s/" "-v"

log_success "Smoke tests completed successfully!"
log_note "Note: Behavioral/timing tests (pod deletion, crash recovery) are in test_crash_recovery_manual.py"
log_note "To run manual tests: pytest test_k8s/test_crash_recovery_manual.py -v -s -m \"\""
echo ""