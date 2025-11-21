# Flask Hello World - Minikube Deployment

Demonstrate deploying a Flask application to a local Kubernetes cluster using Minikube, with comprehensive testing and CI/CD automation.

## Key Takeaways

This project demonstrates production-grade DevOps practices for containerized applications:

| Area | Why It Matters |
|------|----------------|
| **Separation of concerns** | App code, infrastructure manifests, and tests live independently, making the codebase modular and maintainable. |
| **Automated testing** | Tests run at multiple levels (unit tests for Flask, integration tests for Kubernetes) ensuring reliability. |
| **Reproducibility** | Scripts and Makefile create consistent environments across local development, CI/CD, and cloud deployments. |
| **CI/CD integration** | GitHub Actions pipeline automates build, deploy, and validation - see [CI/CD Guide](docs/CI_CD_GUIDE.md) for details. |
| **Cloud-readiness** | The same Kubernetes manifests work for both local Minikube and cloud platforms (EKS, GKE, AKS). |

---

## Quick Start

Note: Use a Python virtual environment for development and testing.
```bash
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

```bash
# Install Flask app dependencies
pip install -r app/requirements.txt

# Install testing dependencies
pip install pytest requests yamllint
```

**Required packages:**
- `pytest` - Test framework for running unit and integration tests
- `requests` - HTTP library for testing service endpoints
- Flask dependencies from `app/requirements.txt`

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

### Option A: Direct Access (without Ingress)
If you want to access the app via NodePort (simpler, for quick testing):

1. Change Service type back to NodePort in `k8s/service.yaml`:
```yaml
spec:
  type: NodePort  # Change from ClusterIP to NodePort
```

2. Deploy:
```
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

3. Access via: `minikube service hello-flask --url`

### Option B: Using Ingress (production-like setup)
For a more production-like setup with Ingress:

1. Setup Ingress controller (only needed once):
```
bash scripts/setup_ingress.sh
```
This enables nginx ingress on Minikube and configures `/etc/hosts`.

2. Deploy application with Ingress:
```
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

3. Wait for Ingress to be ready:
```
kubectl get ingress hello-flask-ingress -w
```
Wait until you see an ADDRESS assigned (Ctrl+C to exit).

4. Access via: `http://hello-flask.local`

Check that Pods are running:
```
kubectl get pods
kubectl get deployments
kubectl get svc
kubectl get ingress
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
APP_ENV=local
LOG_LEVEL=debug
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

## Test Liveness Probe (Self-Healing)

The deployment includes a liveness probe that monitors the health of each pod. If a pod becomes unhealthy or crashes, Kubernetes automatically restarts the container. You can manually test this self-healing behavior:

### Method 1: Delete a Pod (Recommended)
Watch Kubernetes automatically recreate the deleted pod to maintain the desired replica count:

```bash
# Watch pods in real-time (in one terminal)
kubectl get pods -w

# In another terminal, delete one pod
kubectl delete pod <pod-name>
# Example: kubectl delete pod hello-flask-5d856bb855-b7jwp
```

**What you'll see:**
- The deleted pod enters `Terminating` state
- Kubernetes immediately creates a new pod to maintain 2 replicas
- The new pod goes through: `ContainerCreating` → `Running`
- Total time: typically 5-10 seconds

### Method 2: Simulate App Crash
Simulate an application crash by killing the Flask process inside the container:

```bash
# Get a pod name
POD=$(kubectl get pods -l app=hello-flask -o jsonpath="{.items[0].metadata.name}")
echo "Testing pod: $POD"

# Watch the pod status in real-time
kubectl get pod $POD -w &

# Kill the main process (PID 1) inside the container
# Note: Use 'bash -c' because the kill command is a bash builtin
# Use -9 (SIGKILL) to force kill the process
kubectl exec $POD -- bash -c "kill -9 1"
```

**What you'll see:**
- The container immediately terminates
- The liveness probe detects the app is not responding on port 5000
- After 3 consecutive failed checks (with current settings: up to 55-65 seconds), Kubernetes restarts the container
- Pod shows `RESTARTS` count incremented
- The pod stays in `Running` state (container restart, not pod recreation)

**Why does it take so long?**
With the current liveness probe settings:
- `periodSeconds: 10` - Checks every 10 seconds
- `timeoutSeconds: 5` - Waits 5 seconds for response
- `failureThreshold: 3` - Needs 3 consecutive failures

Time calculation: Initial check (0-10s) + (timeout 5s + period 10s) × 3 failures = up to 55-65 seconds total

**Alternative - More visible crash simulation:**
To see a more gradual failure and recovery, you can crash Python instead:
```bash
kubectl exec $POD -- bash -c "pkill -9 python"
# or
kubectl exec $POD -- bash -c "python -c 'import os; os._exit(1)'"
```

### Verify Liveness Probe Configuration
Check the liveness probe settings in your running pod:

```bash
kubectl describe pod <pod-name> | grep -A 10 "Liveness:"
```

**Expected output:**
```
Liveness:       http-get http://:5000/ delay=10s timeout=5s period=10s #success=1 #failure=3
```

This means:
- **Initial delay:** 10 seconds after container starts
- **Check interval:** Every 10 seconds
- **Timeout:** 5 seconds per check
- **Failure threshold:** Restart after 3 consecutive failures

### Check Pod Events for Liveness Failures
If you simulated a crash, you can see the liveness probe failures in the pod events:

```bash
kubectl describe pod <pod-name> | grep -A 20 "Events:"
```

Look for events like:
- `Unhealthy`: Liveness probe failed
- `Killing`: Container being killed
- `Started`: Container restarted successfully

## Run Tests

### Application Unit Tests
```bash
pytest app/tests/ -v
```
Tests the Python/Flask application logic independently of Kubernetes.

### Kubernetes Integration Tests

See the **[Testing](#testing)** section below for detailed test commands and organization.

## Access the App Locally

### With Ingress (Option B):
If you deployed with Ingress:
```bash
curl http://hello-flask.local
# or open http://hello-flask.local in browser
```

### Without Ingress (Option A - NodePort):

#### Method 1: Minikube service URL:
```bash
minikube service hello-flask --url
# Opens the service in browser or shows URL like http://192.168.49.2:32000
```

#### Method 2: Port-forward:
```bash
kubectl port-forward svc/hello-flask 5000:5000
# Then open http://localhost:5000
```

## Clean Up Local Minikube Resources
```bash
kubectl delete -f k8s/ingress.yaml     # if using Ingress
kubectl delete -f k8s/service.yaml
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/secret.yaml
minikube stop
```

## Troubleshooting

### Local Testing Issues

**Problem: Getting 404 when accessing Minikube IP directly**

If you try to access the app via `http://$(minikube ip)` and get a 404:

```bash
curl http://192.168.49.2
# Returns: 404 Not Found
```

**Cause:** Nginx Ingress uses the `Host` HTTP header for routing. When you access via IP, it doesn't match the configured hostname.

**Solutions:**

1. **Use the configured hostname** (recommended for local dev):
   ```bash
   curl http://hello-flask.local
   # Make sure /etc/hosts is configured (run scripts/setup_ingress.sh)
   ```

2. **Send the correct Host header**:
   ```bash
   curl -H "Host: hello-flask.local" http://$(minikube ip)
   # This works! Nginx sees the correct host header
   ```

3. **Use port-forward** (bypasses Ingress):
   ```bash
   kubectl port-forward svc/hello-flask 5000:5000
   curl http://localhost:5000
   ```

**Note:** The tests automatically handle this by sending the correct `Host` header when needed!

### CI/CD Pipeline Issues

If `test_service_reachable` fails in GitHub Actions:

1. **Check the workflow logs** for:
   - Ingress controller status
   - Ingress address assignment
   - Minikube IP
   - Service and pod status

2. **Common issue**: Ingress hostname not resolving in CI
   - **Solution**: The test automatically uses Minikube IP in CI/CD environments
   - No `/etc/hosts` configuration needed in GitHub Actions

3. **Debug locally**: Run the same sequence as CI/CD:
   ```bash
   minikube start
   minikube addons enable ingress
   kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=180s
   bash scripts/deploy_local.sh
   pytest test_k8s/ -v
   ```

4. **Manual verification** in CI/CD or locally:
   ```bash
   # Check Minikube IP
   minikube ip
   
   # Test with correct Host header (required for Ingress)
   curl -H "Host: hello-flask.local" http://$(minikube ip)
   
   # Or use hostname if /etc/hosts is configured
   curl http://hello-flask.local
   
   # Check ingress status
   kubectl get ingress hello-flask-ingress
   kubectl describe ingress hello-flask-ingress
   ```

For more detailed debugging steps, see [`docs/INGRESS_CI_CD_TROUBLESHOOTING.md`](docs/INGRESS_CI_CD_TROUBLESHOOTING.md).

# Automation Scripts

Modular Bash scripts for common workflows. Each script has a targeted function, making it easy to run only what you need.

**Important:** Start Minikube before running scripts: `minikube start`

## Quick Reference

```bash
# Build & Deploy
bash scripts/build_image.sh         # Build Docker image
bash scripts/deploy_local.sh        # Deploy with Ingress
bash scripts/delete_local.sh        # Cleanup resources

# Testing
bash scripts/unit_tests.sh          # App unit tests
bash scripts/k8s_tests.sh           # K8s integration tests (automated)
bash scripts/smoke_test.sh          # Quick validation (automated tests)
bash scripts/liveness_test.sh       # Liveness probe tests (see modes below)

# Utilities
bash scripts/port_forward.sh        # Forward to localhost:8080
bash scripts/minikube_service_url.sh # Get service access URL
bash scripts/setup_ingress.sh       # Setup Ingress controller
```

### Liveness Test Modes
```bash
bash scripts/liveness_test.sh           # Automated config tests (default)
bash scripts/liveness_test.sh --manual  # Manual behavioral tests (slow)
bash scripts/liveness_test.sh --config  # Config check only
```

## Makefile Shortcuts

```bash
# Build & Deploy
make build           # Build Docker image
make deploy          # Deploy to cluster
make delete          # Cleanup

# Testing
make unit-tests      # Run unit tests
make k8s-tests       # Run K8s tests
make smoke-test      # Quick validation

# Validation (before push)
make validate-repo      # Check repository structure
make validate-workflow  # Check GitHub Actions config
make validate-all       # Run all validations

# Composite targets
make test-all        # Run all tests
make full-deploy     # Build → deploy → smoke test
make help            # Show all commands
```

📚 **For detailed script documentation, usage examples, and troubleshooting**, see [`scripts/README.md`](scripts/README.md)

---

## Testing

### Quick Test Commands

```bash
# Run all automated tests (excludes manual and educational tests)
pytest test_k8s/ -v -m 'not manual and not educational'

# Run all automated tests (includes educational tests)
pytest test_k8s/ -v -m 'not manual'

# Run specific test categories
pytest test_k8s/ -v -m ingress        # Ingress tests only
pytest test_k8s/ -v -m educational    # Educational tests only (hostname routing, consistency, load balancing)
pytest test_k8s/ -v -m nodeport       # NodePort tests only
pytest test_k8s/ -v -m manual         # Manual tests (slow, timing-dependent)

# Run specific test file
pytest test_k8s/test_deployment.py -v

# Simulate CI/CD environment (uses Minikube IP + Host header)
CI=true pytest test_k8s/test_service_ingress.py -v -s
```

**Or use Makefile shortcuts:**
```bash
make k8s-tests           # All automated K8s tests (includes educational)
make educational-tests   # Educational Ingress tests only
make ingress-tests       # All Ingress tests (basic + educational)
```

### Test Organization

The test suite uses:
- **Shared utilities** (`test_k8s/utils.py`) - 20+ reusable functions for Kubernetes operations
- **Pytest fixtures** (`test_k8s/conftest.py`) - 10+ fixtures for automated test setup
- **Custom markers** - Categorize tests for selective execution (`@pytest.mark.ingress`, `@pytest.mark.nodeport`, `@pytest.mark.manual`)

📚 **For complete test architecture, utilities reference, and debugging guide**, see [`test_k8s/README.md`](test_k8s/README.md)

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

- **[Documentation Index](docs/README.md)** - Complete documentation overview
- **CI/CD & Automation:**
  - [CI/CD Guide](docs/CI_CD_GUIDE.md) - Pipeline overview, GitHub CLI usage, manual testing
  - [CI/CD Troubleshooting](docs/INGRESS_CI_CD_TROUBLESHOOTING.md) - Ingress and pipeline debugging
  - [Scripts Guide](scripts/README.md) - Automation scripts and service access
- **Test Suite:**
  - [Test Architecture](docs/testing/TEST_ARCHITECTURE.md) - Test design and utilities
  - [Test Refactoring](docs/testing/TEST_REFACTORING.md) - Recent improvements
  - [Test Usage Guide](test_k8s/README.md) - How to run tests
  - [Educational Tests](docs/EDUCATIONAL_TESTS.md) - Learn Ingress concepts through hands-on testing
  - [Educational Tests Quick Reference](docs/EDUCATIONAL_TESTS_QUICKREF.md) - Quick commands
- **Scripts:**
  - [Scripts Guide](scripts/README.md) - Complete script reference and usage
  - [Script Integration](docs/testing/SCRIPT_INTEGRATION.md) - Script integration with pytest markers
- **Operations:**
  - [Ingress Guide](docs/INGRESS_404_EXPLAINED.md) - Ingress issues and troubleshooting
  - [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md) - Pre-push validation and best practices
