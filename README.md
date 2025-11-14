blah blah why move to EKS

Note:     
Use a python virtual environment for development and testing.
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

```bash
# Install Flask app dependencies
pip install -r app/requirements.txt

# Install testing dependencies
pip install pytest requests
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

## Run Application-Level Unit Tests
```
pytest app/tests/ -v
```

* Tests the Python/Flask application logic independently of Kubernetes.
* Example output: `test_app.py::test_hello_route PASSED`

## Run Kubernetes-Level Tests

These tests check that your deployment and services are working in the cluster.

**✅ Tests work with BOTH NodePort and Ingress deployments!**

```
pytest test_k8s/ -v
```

### What the tests do:

* **`test_deployment.py`** → Verifies Pods are Running
  - ✅ Works with both NodePort and Ingress

* **`test_configmap.py`** → Verifies ConfigMap environment variables
  - ✅ Works with both NodePort and Ingress

* **`test_service_access.py`** → Verifies service endpoint responds
  - ✅ **Auto-detects service type** (NodePort or ClusterIP)
  - For NodePort: Uses `minikube service hello-flask --url`
  - For ClusterIP + Ingress: Tests via Ingress host (e.g., `http://hello-flask.local`)

* **`test_ingress.py`** → Verifies Ingress configuration (if deployed)
  - ⚠️ Only runs when Ingress is deployed (skips otherwise)
  - Checks Ingress rules, backend service, and address assignment

### Running specific tests:

```bash
# Run all K8s tests
pytest test_k8s/ -v

# Run only deployment tests
pytest test_k8s/test_deployment.py -v

# Run only service access tests
pytest test_k8s/test_service_access.py -v

# Run only ingress tests (when using Ingress)
pytest test_k8s/test_ingress.py -v

# Simulate CI/CD environment (uses Minikube IP + Host header)
CI=true pytest test_k8s/test_service_access.py -v -s
```

**Note:** Tests automatically detect the environment:
- **Local**: Uses `http://hello-flask.local` (requires `/etc/hosts` configured)
- **CI/CD**: Uses `http://<minikube-ip>` with `Host: hello-flask.local` header

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

### With Ingress (Option B):
If you deployed with Ingress:
```
curl http://hello-flask.local
# or open http://hello-flask.local in browser
```

### Without Ingress (Option A - NodePort):

#### Method 1: Minikube service URL:
```
minikube service hello-flask --url
# Opens the service in browser or shows URL like http://192.168.49.2:32000
```

#### Method 2: Port-forward:
```
kubectl port-forward svc/hello-flask 5000:5000
# Then open http://localhost:5000
```

## Clean Up Local Minikube Resources
```
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

For more detailed debugging steps, see [`docs/DEBUGGING_CI_CD.md`](docs/DEBUGGING_CI_CD.md).

## Deploying to AWS EKS (Production)

When deploying to EKS, the Ingress setup is different:

### Prerequisites for EKS
1. **AWS Load Balancer Controller** installed in your EKS cluster
2. **IAM permissions** for the controller to create ALBs
3. **DNS configuration** (Route53 or similar)
4. **SSL certificate** in AWS Certificate Manager (optional, for HTTPS)

### EKS Deployment Steps

1. **Install AWS Load Balancer Controller** (one-time setup):
```bash
# Follow AWS documentation to install the controller
# https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html
```

2. **Update Ingress for EKS**:
Edit `k8s/ingress.yaml` and uncomment the EKS section (or create a separate file):
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hello-flask-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS": 443}]'
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:region:account:certificate/id
    alb.ingress.kubernetes.io/ssl-redirect: '443'
spec:
  rules:
  - host: your-domain.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: hello-flask
            port:
              number: 5000
```

3. **Deploy to EKS**:
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

4. **Get ALB DNS name**:
```bash
kubectl get ingress hello-flask-ingress
# Shows ADDRESS with ALB DNS name
```

5. **Configure DNS**: Point your domain to the ALB DNS using a CNAME record in Route53.

### Key Differences: Minikube vs EKS

| Feature | Minikube (Local) | EKS (Production) |
|---------|------------------|------------------|
| Ingress Controller | nginx | AWS Load Balancer Controller |
| Load Balancer | None (uses minikube IP) | Application Load Balancer (ALB) |
| DNS | /etc/hosts entry | Route53 or external DNS |
| SSL/TLS | Manual cert or none | AWS Certificate Manager |
| Cost | Free | Pay for ALB + data transfer |
| Access | http://hello-flask.local | https://your-domain.com |


# Automation scripts
Break the workflow into modular Bash scripts, each with a targeted function, so you can run only what you need.
This is a good structure fpr automation: clean, reusable, and easy to integrate into pipelines.

All scripts run within the cloud environment, remember before running the scripts to initiate the local cloud (`minikube start`), as well as release all resources when done development and testing (`minikube stop`).

## Usage Example
Each script can be run individually:
```
bash scripts/build_image.sh         # Build image
bash scripts/deploy_local.sh        # Deploy app with Ingress
bash scripts/unit_tests.sh          # Run app unit tests
bash scripts/k8s_tests.sh           # Run K8s-level tests
bash scripts/smoke_test.sh          # Run all tests
bash scripts/port_forward.sh        # Forward service to localhost
bash scripts/minikube_service_url.sh # Get service URL (works with both NodePort and Ingress)
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
make minikube-url - Get service URL and access methods
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


# Change logs
* Add Ingress for more production ready code, added extensive and verbose debug logs for reference