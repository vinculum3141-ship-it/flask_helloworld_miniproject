#!/bin/bash
# -----------------------------------------------------------------------------
# Manual helper: Port-forward the hello-flask Kubernetes service for a quick
# local check. Not used by CI.
#
# CI coverage: Service reachability is validated in pytest via
#   flask-k8s/test_k8s/test_service_access.py
#
# Requirements:
# - Minikube is running and configured (uses `minikube kubectl -- ...`).
# - Service `svc/hello-flask` exists in the default namespace.
#
# Behavior:
# - Starts `kubectl port-forward` (5000:5000) in the background,
#   waits briefly, curls http://localhost:5000, then kills the forward.
# - Curl failures are logged but do not cause a non-zero exit code.
#
# Usage:
#   bash scripts/port_forward.sh
#
# Note: For an interactive tunnel, run the port-forward manually and stop with
# Ctrl+C:
#   minikube kubectl -- port-forward svc/hello-flask 5000:5000
# -----------------------------------------------------------------------------
set -euo pipefail

port_forward_app() {
    echo "[INFO] Forwarding port 5000 from hello-flask service to localhost..."
    echo "[INFO] Starting port forward in background..."
    minikube kubectl -- port-forward svc/hello-flask 5000:5000 &
    PORT_FORWARD_PID=$!

    echo "[INFO] Port forward PID: $PORT_FORWARD_PID"
    echo "[INFO] Waiting 3 seconds for port forward to establish..."
    sleep 3

    echo "[INFO] Testing the service..."
    curl -s http://localhost:5000 || echo "[ERROR] Curl failed"

    echo "[INFO] Killing port forward process..."
    kill $PORT_FORWARD_PID || true

    echo "[INFO] Done!"
}

# Run function
port_forward_app
