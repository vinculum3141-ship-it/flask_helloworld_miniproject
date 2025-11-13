#!/bin/bash

# -----------------------------------------------------------------------------
# NOTE: Example helper script (manual use)
#
# This script demonstrates building the Docker image inside Minikube's Docker
# daemon for local/manual testing. It is NOT invoked by the CI workflows.
#
# In CI, the image build is handled directly in the workflow steps (pointing the
# Docker CLI to Minikube and running `docker build` inline). The workflow also
# manages tags (e.g., both `:latest` and `:${GITHUB_SHA}`) and logging.
#
# Use this script locally to validate a build in your Minikube environment. The
# Deployment in k8s/deployment.yaml references `hello-flask:latest`, so this
# script tags `:latest` only.
# -----------------------------------------------------------------------------

set -e

# Function: build Docker image for Minikube
build_image() {
    echo "[INFO] Switching to Minikube Docker environment..."
    eval $(minikube docker-env)

    echo "[INFO] Building Docker image 'hello-flask:latest'..."
    docker build -t hello-flask:latest ./app

    echo "[INFO] Docker image built successfully."
    docker images | grep hello-flask

}

# Run function
build_image
