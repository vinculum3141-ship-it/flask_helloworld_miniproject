#!/bin/bash
set -euo pipefail

cleanup_app() {
    echo "[INFO] Deleting Service, Deployment, ConfigMap, Secret..."
    minikube kubectl -- delete -f k8s/service.yaml --ignore-not-found
    minikube kubectl -- delete -f k8s/deployment.yaml --ignore-not-found
    minikube kubectl -- delete -f k8s/configmap.yaml --ignore-not-found
    minikube kubectl -- delete -f k8s/secret.yaml --ignore-not-found

    echo "[INFO] Cleanup complete."
}

# Run function
cleanup_app
