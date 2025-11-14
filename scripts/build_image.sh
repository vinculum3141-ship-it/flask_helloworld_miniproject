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

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  Building Docker Image${NC}"
    echo -e "${BLUE}================================================${NC}"
}

# Function: build Docker image for Minikube
build_image() {
    echo -e "\n${GREEN}[INFO] Switching to Minikube Docker environment...${NC}"
    eval $(minikube docker-env)

    echo -e "${GREEN}[INFO] Building Docker image 'hello-flask:latest'...${NC}"
    docker build -t hello-flask:latest ./app

    echo -e "\n${GREEN}[INFO] Docker image built successfully.${NC}"
    echo -e "${YELLOW}Available images:${NC}"
    docker images | grep hello-flask || echo "No hello-flask images found"
}

# Run
print_header
build_image
echo -e "\n${GREEN}✅ Image build completed!${NC}\n"
