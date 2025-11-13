#!/bin/bash
set -e

run_unit_tests() {
    echo "[INFO] Running Python unit tests..."
    pytest app/tests/ -v
}

# Run function
run_unit_tests
