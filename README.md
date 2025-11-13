If you’re approaching this as a test engineer, you’re thinking not *just how to deploy*, but *how to structure, validate, and maintain* the project properly — including tests, configuration, and reproducibility.

Let’s go over what the file/package structure should look like when a **test engineer** (QA or SDET) organizes the “Mini Task” project — a simple app deployed to **Kubernetes (Minikube/EKS)** with **testability and CI/CD readiness** in mind.

Note:     
Use a python virtual environment for development and testing. In your working directory `flask-k8s`:
```
python3 -m venv .venv
source .venv/bin/activate
```

# Step-by-step commands (run in a terminal)

## Pre-requisites

Make sure you have installed:

| Tool | Command to check |
|------|-----------------|
| Python 3.11+ | `python --version` |
| pip | `pip --version` |
| Docker | `docker --version` |
| Minikube | `minikube version` |
| kubectl | `kubectl version --client` |

Also, ensure Python packages for testing are installed:

```
pip install -r app/requirements.txt pytest requests
```

## Start Minikube
```
minikube start
minikube status
```

* This starts a single-node Kubernetes cluster locally.
* `minikube status` confirms that the cluster is running.

## Build the Docker image for the app
```
eval $(minikube docker-env)
docker build -t hello-flask:latest ./app
```

Ensures the image is available to the Minikube cluster without pushing to Docker Hub.
```
docker images | grep hello-flask
```

## Deploy ConfigMap and Secret (optional for advanced testing)
```
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
```

## Deploy the app to Kubernetes
```
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Check that Pods are running:
```
kubectl get pods
kubectl get deployments
kubectl get svc
```

Wait until Pods show `STATUS=Running`.
```
kubectl get pods -o wide -l app=hello-flask
kubectl logs deploy/hello-flask
```
If ConfigMap and Secret was deployed, confirm environment variables inside a running Pod:
```
POD=$(kubectl get pods -l app=hello-flask -o jsonpath="{.items[0].metadata.name}")
echo $POD
kubectl describe pod $POD | grep Status
kubectl exec -it $POD -- env | grep -E 'APP_ENV|LOG_LEVEL|API_KEY|DB_PASSWORD|CUSTOM_MESSAGE'
```

Expected output:
```
APP_ENV=staging
LOG_LEVEL=info
FEATURE_FLAG_GREETING=true
API_KEY=somesecretkey
DB_PASSWORD=password123
CUSTOM_MESSAGE=Deployed via ConfigMap + Secret
```

Note: Kubernetes Secrets must use base64 encoding.
To generate encoded values:
```
echo -n "somesecretkey" | base64
```

## Run Application-Level Unit Tests
```
pytest app/tests/ -v
```

* Tests the Python/Flask application logic independently of Kubernetes.
* Example output: `test_app.py::test_hello_route PASSED`

## Run Kubernetes-Level Tests
These tests check that your deployment and services are working in the cluster.
```
pytest test_k8s/ -v
```

Examples of what happens:
* `test_deployment.py` → verifies Pods are Running.
* `test_service_access.py` → verifies the service endpoint responds (`minikube service hello-flask --url`).

## Run Smoke Tests (Optional Script)
The `smoke_test.sh` script runs all K8s tests automatically:
```
bash scripts/smoke_test.sh
```

Output will show:
* Deployment checks
* Pod health
* Service accessibility

## Access the App Locally
### Option 1: Minikube service URL:
```
minikube service hello-flask --url
# Opens the service in browser or shows URL like http://192.168.49.2:32000
```

### Option 2: Port-forward:
```
kubectl port-forward svc/hello-flask 5000:5000
# Then open http://localhost:5000
```

## Clean Up Local Minikube Resources
```
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/secret.yaml
minikube stop
```


# Automation scripts
Break the workflow into modular Bash scripts, each with a targeted function, so you can run only what you need.
This is a good structure fpr automation: clean, reusable, and easy to integrate into pipelines.

All scripts run within the cloud environment, remember before running the scripts to initiate the local cloud (`minikube start`), as well as release all resources when done development and testing (`minikube stop`).

## Usage Example
Each script can be run individually:
```
bash scripts/build_image.sh         # Build image
bash scripts/deploy_local.sh        # Deploy app
bash scripts/unit_tests.sh          # Run app unit tests
bash scripts/k8s_tests.sh           # Run K8s-level tests
bash scripts/smoke_test.sh          # Run all tests
bash scripts/port_forward.sh        # Forward service to localhost
bash scripts/minikube_service_url.sh # Get service URL
bash scripts/delete_local.sh        # Cleanup
```
## Convenience Shortcuts (Makefile)

Individual Script Targets:
```
make build - Build Docker image
make deploy - Deploy to local cluster
make unit-tests - Run unit tests
make k8s-tests - Run k8s integration tests
make smoke-test - Run smoke tests
make port-forward - Forward service port to localhost
make minikube-url - Get minikube service URL
```
Composite Targets:
```
make test-all - Run both unit and k8s tests
make full-deploy - Complete workflow: build → deploy → smoke test
```
Utility:
```
make help - Show all available commands
```

Clean Up:
```
make delete - Delete local deployment
```