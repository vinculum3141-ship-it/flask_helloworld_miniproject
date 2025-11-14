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

# Run all K8s tests except manual tests (fast configuration checks only)
# Timing-dependent behavioral tests are excluded via @pytest.mark.manual
run_pytest "test_k8s/" "-v -m 'not manual'"

log_success "Smoke tests completed successfully!"
log_note "Note: Manual tests excluded (pod deletion, crash recovery)."
log_note "To run manual tests: pytest test_k8s/ -v -m manual"
echo ""