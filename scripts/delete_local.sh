#!/bin/bash
set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  Cleaning Up Deployment${NC}"
    echo -e "${BLUE}================================================${NC}"
}

cleanup_app() {
    echo -e "\n${GREEN}[INFO] Deleting Ingress...${NC}"
    minikube kubectl -- delete -f k8s/ingress.yaml --ignore-not-found
    
    echo -e "${GREEN}[INFO] Deleting Service...${NC}"
    minikube kubectl -- delete -f k8s/service.yaml --ignore-not-found
    
    echo -e "${GREEN}[INFO] Deleting Deployment...${NC}"
    minikube kubectl -- delete -f k8s/deployment.yaml --ignore-not-found
    
    echo -e "${GREEN}[INFO] Deleting ConfigMap...${NC}"
    minikube kubectl -- delete -f k8s/configmap.yaml --ignore-not-found
    
    echo -e "${GREEN}[INFO] Deleting Secret...${NC}"
    minikube kubectl -- delete -f k8s/secret.yaml --ignore-not-found

    echo -e "${GREEN}[INFO] Cleanup complete.${NC}"
}

# Run
print_header
cleanup_app
echo -e "\n${GREEN}✅ All resources deleted!${NC}"
echo -e "${YELLOW}Minikube cluster is still running. Use 'minikube stop' to shut it down.${NC}\n"
