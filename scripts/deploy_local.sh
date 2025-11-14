#!/bin/bash
set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

LOG_DIR="${PWD}/logs"
mkdir -p "${LOG_DIR}"

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  Deploying to Minikube${NC}"
    echo -e "${BLUE}================================================${NC}"
}

collect_diagnostics() {
  echo -e "\n${RED}=== COLLECTING DIAGNOSTICS ===${NC}"
  echo "Timestamp: $(date -u +'%Y-%m-%dT%H:%M:%SZ')" | tee "${LOG_DIR}/diag.txt"

  echo -e "\n--- kubectl cluster-info ---" | tee -a "${LOG_DIR}/diag.txt"
  minikube kubectl -- cluster-info 2>&1 | tee -a "${LOG_DIR}/diag.txt"

  echo -e "\n--- kubectl get nodes -o wide ---" | tee -a "${LOG_DIR}/diag.txt"
  minikube kubectl -- get nodes -o wide 2>&1 | tee -a "${LOG_DIR}/diag.txt"

  echo -e "\n--- kubectl get pods -A -o wide ---" | tee -a "${LOG_DIR}/diag.txt"
  minikube kubectl -- get pods -A -o wide 2>&1 | tee -a "${LOG_DIR}/diag.txt"

  echo -e "\n--- kubectl describe pods (app label) ---" | tee -a "${LOG_DIR}/diag.txt"
  minikube kubectl -- describe pod -l app=hello-flask --all-namespaces 2>&1 | tee -a "${LOG_DIR}/diag.txt" || true

  echo -e "\n--- kubectl get events (last 200) ---" | tee -a "${LOG_DIR}/diag.txt"
  minikube kubectl -- get events -A --sort-by='.metadata.creationTimestamp' 2>&1 | tail -n 200 | tee -a "${LOG_DIR}/diag.txt" || true

  PODS=$(minikube kubectl -- get pods -l app=hello-flask -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' || true)
  if [[ -n "${PODS}" ]]; then
    for p in ${PODS}; do
      echo -e "\n--- logs for pod: ${p} ---" | tee -a "${LOG_DIR}/diag.txt"
      CONTAINERS=$(minikube kubectl -- get pod "${p}" -o jsonpath='{.spec.containers[*].name}' || true)
      for c in ${CONTAINERS}; do
        echo "--- container: ${c} ---" >> "${LOG_DIR}/diag.txt"
        minikube kubectl -- logs "${p}" -c "${c}" --tail=500 2>&1 | tee -a "${LOG_DIR}/diag.txt" || true
      done
    done
  else
    echo "No pods found with label app=hello-flask" | tee -a "${LOG_DIR}/diag.txt"
  fi

  echo -e "\n--- minikube logs (tail 500) ---" | tee -a "${LOG_DIR}/diag.txt"
  minikube logs 2>&1 | tail -n 500 | tee -a "${LOG_DIR}/diag.txt" || true

  echo -e "\n--- minikube image list ---" | tee -a "${LOG_DIR}/diag.txt"
  minikube image list 2>&1 | tee -a "${LOG_DIR}/diag.txt" || true

  echo -e "\n--- docker images (current DOCKER env) ---" | tee -a "${LOG_DIR}/diag.txt"
  docker images --format '{{.Repository}}:{{.Tag}} {{.ID}} {{.Size}}' 2>&1 | tee -a "${LOG_DIR}/diag.txt" || true

  echo -e "${YELLOW}Diagnostics collected in ${LOG_DIR}/diag.txt${NC}"
}

trap 'rc=$?; echo -e "${RED}ERROR: deploy_local.sh failed with exit ${rc}${NC}"; collect_diagnostics; exit ${rc}' ERR

deploy_app() {
    echo -e "\n${GREEN}[INFO] Applying ConfigMap...${NC}"
    minikube kubectl -- apply -f k8s/configmap.yaml

    echo -e "${GREEN}[INFO] Applying Secret...${NC}"
    minikube kubectl -- apply -f k8s/secret.yaml

    echo -e "${GREEN}[INFO] Deploying Deployment & Service...${NC}"
    minikube kubectl -- apply -f k8s/deployment.yaml
    minikube kubectl -- apply -f k8s/service.yaml

    echo -e "${GREEN}[INFO] Deploying Ingress...${NC}"
    minikube kubectl -- apply -f k8s/ingress.yaml

    echo -e "${GREEN}[INFO] Waiting for deployment rollout (timeout 5m)...${NC}"
    # add a timeout so this step doesn't hang indefinitely
    minikube kubectl -- rollout status deployment/hello-flask --timeout=5m

    echo -e "${GREEN}[INFO] App deployed successfully.${NC}"
}

# Run
print_header
deploy_app
echo -e "\n${GREEN}✅ Deployment completed!${NC}"
echo -e "${YELLOW}Run 'kubectl get pods' to check pod status${NC}\n"
