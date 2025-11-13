#!/bin/bash
set -e

# Run ALL tests (both Flask app and k8s tests)
pytest

# Run just app tests
pytest app/tests/

# Run just k8s tests  
pytest test_k8s/

# Run a specific test
pytest test_k8s/test_configmap.py::test_configmap_applied