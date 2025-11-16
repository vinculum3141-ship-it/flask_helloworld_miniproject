# Troubleshooting: Ingress in CI/CD Environments

## Overview

This comprehensive guide explains how to troubleshoot Kubernetes Ingress issues in CI/CD environments, with a focus on understanding Host header routing and solving common pipeline failures.

---

## The Problem: Ingress Host Header Routing

When accessing an Ingress via IP address instead of hostname, nginx returns 404 because the Host header doesn't match the configured routing rule.

### Root Cause

```bash
# This fails with 404:
curl http://192.168.49.2
# Because nginx receives: Host: 192.168.49.2 (doesn't match routing rule)

# This works with 200:
curl -H "Host: hello-flask.local" http://192.168.49.2
# Because nginx receives: Host: hello-flask.local (matches routing rule!)
```

### Why This Matters in CI/CD

1. **Ingress configuration** specifies `host: hello-flask.local` in the routing rule
2. **Local development** has `/etc/hosts` configured, so `hello-flask.local` resolves
3. **CI/CD environments** (like GitHub Actions) don't have `/etc/hosts` configured
4. **Solution**: Use one of three approaches (see Solutions section below)

### Common Symptoms

```
AssertionError: Failed to reach service at http://hello-flask.local
```

Or:

```
curl: (6) Could not resolve host: hello-flask.local
```

---

## Solutions for CI/CD Environments

### Solution 1: Use Minikube IP with Host Header (Recommended - Current Implementation)

The test suite automatically detects CI/CD environment and uses Minikube IP with the correct Host header.

**How it works:**

The `is_ci_environment()` utility function (in `test_k8s/utils.py`) detects GitHub Actions:

```python
def is_ci_environment() -> bool:
    """Detect if running in CI/CD environment."""
    return os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'
```

**Implementation in tests:**
```python
# In CI/CD Environment
# URL: http://192.168.49.2
# Headers: {'Host': 'hello-flask.local'}

# In Local Development
# URL: http://hello-flask.local
# Headers: {} (no special headers needed)
```

This is used by:
- `test_k8s/test_service_ingress.py` - Ingress-based access tests
- `test_k8s/test_service_access.py` - Legacy file (backward compatibility)

### Solution 2: Configure /etc/hosts in CI/CD Workflow

Add `/etc/hosts` entry in the GitHub Actions workflow before running tests:

```yaml
- name: Configure /etc/hosts for Ingress
  if: ${{ github.event_name != 'pull_request' }}
  run: |
    INGRESS_IP=$(kubectl get ingress hello-flask-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "127.0.0.1")
    echo "$INGRESS_IP hello-flask.local" | sudo tee -a /etc/hosts
    echo "Added to /etc/hosts: $INGRESS_IP hello-flask.local"
    cat /etc/hosts | grep hello-flask
```

**Pros:** Tests work exactly as in local development  
**Cons:** Requires workflow modification, may need sudo permissions

### Solution 3: Port-Forward in Tests

Use port-forwarding instead of relying on DNS or Ingress:

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

**Pros:** Bypasses Ingress routing entirely  
**Cons:** Doesn't test Ingress configuration, adds complexity

---

## Understanding Ingress Host-Based Routing

Nginx Ingress Controller uses the `Host` HTTP header to route requests to the correct backend service.

### Ingress Configuration

```yaml
# In k8s/ingress.yaml:
spec:
  rules:
  - host: hello-flask.local  # This matches against the Host header
    http:
      paths:
      - path: /
        backend:
          service:
            name: hello-flask
```

### How Routing Works

**Request without matching Host header:**
```bash
curl http://192.168.49.2
# HTTP Request:
#   GET / HTTP/1.1
#   Host: 192.168.49.2
# 
# Nginx Response: 404 Not Found
# Reason: No routing rule matches "192.168.49.2"
```

**Request with matching Host header:**
```bash
curl -H "Host: hello-flask.local" http://192.168.49.2
# HTTP Request:
#   GET / HTTP/1.1
#   Host: hello-flask.local
# 
# Nginx Response: 200 OK
# Reason: Matches the routing rule for "hello-flask.local"
```

---

## Testing Ingress Access

### Run Tests Locally

```bash
# Uses hostname (via /etc/hosts)
pytest test_k8s/test_service_ingress.py -v -s
```

### Simulate CI Environment

```bash
# Forces IP-based access with Host header
export CI=true
pytest test_k8s/test_service_ingress.py -v -s
```

### Test Locally with Same Sequence as CI

Run the exact same sequence locally to reproduce CI behavior:

```bash
minikube start
minikube addons enable ingress
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=180s
bash scripts/deploy_local.sh

# Check if /etc/hosts is configured
grep hello-flask.local /etc/hosts

# Run tests
pytest test_k8s/test_service_ingress.py -v -s
```

### Expected Test Output

**In CI/CD:**
```
Detected CI environment - using Minikube IP with Host header
Using Minikube IP: 192.168.49.2
Setting Host header: hello-flask.local
Testing via Ingress: http://192.168.49.2
✓ Service is reachable
```

**Locally:**
```
Using Ingress hostname: hello-flask.local
Testing via Ingress: http://hello-flask.local
✓ Service is reachable
```

---

## Debugging Ingress Issues

### Quick Debugging Checklist

- [ ] Ingress controller is enabled and ready
- [ ] Ingress resource has an IP address assigned
- [ ] Service is ClusterIP (not NodePort when using Ingress)
- [ ] `/etc/hosts` is configured (local) or Minikube IP is used (CI)
- [ ] Pods are running and ready
- [ ] Test can resolve/reach the URL

### Step-by-Step Debugging

#### 1. Check Ingress Controller Status

```bash
# Verify Ingress controller is running
kubectl get pods -n ingress-nginx

# Expected output:
# NAME                                        READY   STATUS
# ingress-nginx-controller-xxxx               1/1     Running
```

#### 2. Verify Ingress Resource

```bash
# Check Ingress resource exists and has address
kubectl get ingress hello-flask-ingress

# Expected output:
# NAME                  CLASS   HOSTS                 ADDRESS         PORTS
# hello-flask-ingress   nginx   hello-flask.local     192.168.49.2    80
```

#### 3. Test Ingress Access Manually

```bash
# Get Minikube IP
minikube ip

# Test with Host header (should work)
curl -H "Host: hello-flask.local" http://$(minikube ip)

# Or if /etc/hosts is configured:
curl http://hello-flask.local
```

#### 4. Check Backend Pods

```bash
# Verify pods are running
kubectl get pods -l app=hello-flask

# Expected output:
# NAME                           READY   STATUS    RESTARTS
# hello-flask-xxxxxxxxx-xxxxx    1/1     Running   0
```

#### 5. Check Ingress Logs

```bash
# View Ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller --tail=50

# Look for routing decisions and errors
```

#### 6. Describe Ingress Resource

```bash
# Get detailed Ingress information
kubectl describe ingress hello-flask-ingress

# Check:
# - Rules section shows correct host
# - Backend shows correct service
# - Events section for any errors
```

### Add Debug Output to GitHub Actions

Add these commands before running tests in your workflow to get detailed state information:

```yaml
- name: Debug Ingress and Service
  run: |
    echo "=== Minikube IP ==="
    minikube ip
    
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
    
    echo "=== Test DNS resolution ==="
    nslookup hello-flask.local || echo "DNS lookup failed (expected in CI)"
```

### Manual Service Test in CI (Debugging)

If you need to bypass Ingress for debugging, use port-forward:

```yaml
- name: Manual service test (debug)
  run: |
    kubectl port-forward svc/hello-flask 5000:5000 &
    sleep 3
    curl -v http://localhost:5000
    kill %1
```

---

## Common Issues and Solutions

### Issue: 404 Not Found

**Symptom:** `curl http://192.168.49.2` returns 404

**Cause:** Missing Host header

**Solution:** Use Host header: `curl -H "Host: hello-flask.local" http://192.168.49.2`

### Issue: Connection Refused

**Symptom:** `curl: (7) Failed to connect`

**Cause:** Ingress controller not ready or Minikube not running

**Solution:** 
```bash
minikube status
kubectl get pods -n ingress-nginx
```

### Issue: Hostname Not Resolving

**Symptom:** `curl: (6) Could not resolve host: hello-flask.local`

**Cause:** `/etc/hosts` not configured

**Solution:** Add entry or use IP with Host header:
```bash
# Option 1: Configure /etc/hosts
echo "$(minikube ip) hello-flask.local" | sudo tee -a /etc/hosts

# Option 2: Use IP with Host header
curl -H "Host: hello-flask.local" http://$(minikube ip)
```

---

## Related Documentation

- **[Ingress 404 Explained](INGRESS_404_EXPLAINED.md)** - Detailed Ingress routing explanation and troubleshooting
- **[CI/CD Guide](CI_CD_GUIDE.md)** - Complete CI/CD pipeline reference
- **[Test Architecture](testing/TEST_ARCHITECTURE.md)** - Test suite design
- **[Test Usage Guide](../test_k8s/README.md)** - How to run and write tests

## Additional Resources

- [Minikube Ingress Documentation](https://minikube.sigs.k8s.io/docs/handbook/addons/ingress-dns/)
- [GitHub Actions Debugging](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
