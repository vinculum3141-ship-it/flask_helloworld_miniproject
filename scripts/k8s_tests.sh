#!/bin/bash
set -e

run_k8s_tests() {
    echo "[INFO] Running Kubernetes-level tests..."
    pytest test_k8s/ -v
}

# Run function
run_k8s_tests
