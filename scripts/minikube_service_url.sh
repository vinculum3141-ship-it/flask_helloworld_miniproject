#!/bin/bash

# -----------------------------------------------------------------------------
# NOTE: Manual helper script (not used by CI)
#
# This script fetches the Minikube service URL for the `hello-flask` service and
# does a simple curl to it for a quick manual check.
#
# In CI, this functionality is tested via pytest rather than this script:
#   - See: `flask-k8s/test_k8s/test_service_access.py`
#     * Resolves the service URL with `minikube service ... --url`
#     * Asserts the URL is valid and performs an HTTP GET asserting status/content
#
# Use this script locally during development; CI runs stronger assertions in tests.
# -----------------------------------------------------------------------------

set -e

get_service_url() {
    echo "[INFO] Fetching service URL..."
    URL=$(minikube service hello-flask --url)
    echo "[INFO] Access your app at: $URL"
    curl -s $URL || echo "[ERROR] Curl failed"
}

# Run function
get_service_url
