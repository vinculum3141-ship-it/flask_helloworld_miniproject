# Debugging CI/CD Pipeline Failures

## Common Issue: `test_service_reachable` Fails in GitHub Actions

### Problem
When using Ingress with ClusterIP service, the test fails because:
1. The test tries to access `http://hello-flask.local`
2. GitHub Actions runner doesn't have `/etc/hosts` configured
3. DNS resolution fails for the ingress host

### Symptoms
```
AssertionError: Failed to reach service at http://hello-flask.local
```

### Solutions

#### Option 1: Add /etc/hosts Entry in CI/CD (Recommended)
Add this step **before** running K8s tests in `.github/workflows/ci-cd.yml`:

```yaml
- name: Configure /etc/hosts for Ingress
  if: ${{ github.event_name != 'pull_request' }}
  run: |
    INGRESS_IP=$(kubectl get ingress hello-flask-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "127.0.0.1")
    echo "$INGRESS_IP hello-flask.local" | sudo tee -a /etc/hosts
    echo "Added to /etc/hosts: $INGRESS_IP hello-flask.local"
    cat /etc/hosts | grep hello-flask
```

#### Option 2: Use Port-Forward in Tests (Alternative)
Modify the test to use port-forwarding instead of relying on DNS:

```python
def get_ingress_url_via_port_forward():
    """Access Ingress via port-forward (for CI environments)."""
    # Get the ingress nginx controller pod
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", "ingress-nginx", 
         "-l", "app.kubernetes.io/component=controller",
         "-o", "jsonpath={.items[0].metadata.name}"],
        capture_output=True, text=True
    )
    
    if result.returncode == 0 and result.stdout.strip():
        # Use localhost instead of hello-flask.local
        return "http://localhost:8080"  # Requires port-forward setup
    
    return None
```

#### Option 3: Get Minikube IP Directly (Simplest for CI)
Instead of using the hostname, get the Minikube IP and construct the URL:

```python
def get_ingress_url():
    """Get URL from Ingress resource."""
    # For CI/CD: Use Minikube IP directly instead of hostname
    minikube_ip = subprocess.run(
        ["minikube", "ip"],
        capture_output=True, text=True
    ).stdout.strip()
    
    if minikube_ip:
        return f"http://{minikube_ip}"
    
    # Fallback to hostname (for local development)
    return "http://hello-flask.local"
```

### Debugging Steps

#### 1. Check Workflow Logs
Look for these sections in GitHub Actions logs:
- Ingress controller installation
- Ingress address assignment
- Pod readiness
- Test execution output

#### 2. Add Debug Output
Add these commands before running tests in the workflow:

```yaml
- name: Debug Ingress and Service
  run: |
    echo "=== Ingress Status ==="
    kubectl get ingress -A
    kubectl describe ingress hello-flask-ingress
    
    echo "=== Service Status ==="
    kubectl get svc -A
    kubectl describe svc hello-flask
    
    echo "=== Pods Status ==="
    kubectl get pods -A
    kubectl get pods -l app=hello-flask -o wide
    
    echo "=== Ingress Controller Logs ==="
    kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller --tail=50
    
    echo "=== /etc/hosts ==="
    cat /etc/hosts
    
    echo "=== Minikube IP ==="
    minikube ip
    
    echo "=== Test DNS resolution ==="
    nslookup hello-flask.local || echo "DNS lookup failed (expected)"
    ping -c 1 hello-flask.local || echo "Ping failed (expected)"
```

#### 3. Test Locally
Run the exact same sequence locally:

```bash
minikube start
minikube addons enable ingress
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=180s
bash scripts/deploy_local.sh

# Check if /etc/hosts is configured
grep hello-flask.local /etc/hosts

# Run tests
pytest test_k8s/test_service_access.py -v -s
```

#### 4. Manual Test in CI
Access the service using port-forward instead:

```yaml
- name: Manual service test (debug)
  run: |
    kubectl port-forward svc/hello-flask 5000:5000 &
    sleep 3
    curl -v http://localhost:5000
    kill %1
```

### Best Practice: Environment Detection

Update `test_service_access.py` to detect CI environment:

```python
import os

def is_ci_environment():
    """Detect if running in CI/CD environment."""
    return os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'

def get_ingress_url():
    """Get URL from Ingress resource."""
    if is_ci_environment():
        # In CI: Use Minikube IP
        minikube_ip = subprocess.run(
            ["minikube", "ip"],
            capture_output=True, text=True
        ).stdout.strip()
        
        if minikube_ip:
            return f"http://{minikube_ip}"
    
    # Local development: Use hostname
    return "http://hello-flask.local"
```

### Quick Fix Checklist

- [ ] Ingress controller is enabled and ready
- [ ] Ingress resource has an IP address assigned
- [ ] Service is ClusterIP (not NodePort)
- [ ] `/etc/hosts` is configured (local) or Minikube IP is used (CI)
- [ ] Pods are running and ready
- [ ] Test can resolve/reach the URL

### Additional Resources

- [Minikube Ingress Documentation](https://minikube.sigs.k8s.io/docs/handbook/addons/ingress-dns/)
- [GitHub Actions Debugging](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
