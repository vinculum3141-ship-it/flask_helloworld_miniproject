# Understanding the 404 Error with Ingress

## The Problem

When using Ingress with a hostname rule, you get a 404 when accessing via IP address directly.

## Why This Happens

### Ingress Configuration
```yaml
spec:
  ingressClassName: nginx
  rules:
  - host: hello-flask.local  # ← Nginx matches this against the Host header
    http:
      paths:
      - path: /
        backend:
          service:
            name: hello-flask
```

### HTTP Request Flow

#### ❌ Request via IP (404 Not Found)
```
Client → http://192.168.49.2
         │
         ▼
    Nginx Ingress Controller
         │
         ├─ Checks: Host header = "192.168.49.2"
         ├─ Compares with rule: "hello-flask.local"
         ├─ Result: NO MATCH
         │
         ▼
    Returns: 404 Not Found
```

**HTTP Request:**
```http
GET / HTTP/1.1
Host: 192.168.49.2       ← Doesn't match "hello-flask.local"
```

#### ✅ Request via Hostname (200 OK)
```
Client → http://hello-flask.local
         │
         ▼
    Nginx Ingress Controller
         │
         ├─ Checks: Host header = "hello-flask.local"
         ├─ Compares with rule: "hello-flask.local"
         ├─ Result: MATCH! ✓
         │
         ▼
    Routes to: hello-flask Service
         │
         ▼
    Returns: 200 OK (Flask app response)
```

**HTTP Request:**
```http
GET / HTTP/1.1
Host: hello-flask.local  ← Matches rule!
```

#### ✅ Request via IP with Host Header (200 OK)
```
Client → http://192.168.49.2
         + Header: "Host: hello-flask.local"
         │
         ▼
    Nginx Ingress Controller
         │
         ├─ Checks: Host header = "hello-flask.local"  ← From header, not URL!
         ├─ Compares with rule: "hello-flask.local"
         ├─ Result: MATCH! ✓
         │
         ▼
    Routes to: hello-flask Service
         │
         ▼
    Returns: 200 OK (Flask app response)
```

**HTTP Request:**
```http
GET / HTTP/1.1
Host: hello-flask.local  ← Manually set header matches rule!
```

## Solutions

### 1. Local Development (Use Hostname)
```bash
# Setup /etc/hosts
bash scripts/setup_ingress.sh

# Access via hostname
curl http://hello-flask.local
```

### 2. CI/CD Environment (Use IP + Host Header)
```bash
# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

# Send correct Host header
curl -H "Host: hello-flask.local" http://$MINIKUBE_IP
```

### 3. Bypass Ingress (Port Forward)
```bash
# Direct access to service
kubectl port-forward svc/hello-flask 5000:5000
curl http://localhost:5000
```

## How the Tests Handle This

The `test_service_access.py` test automatically:

1. **Detects environment** (local vs CI)
2. **In local dev**: Uses `http://hello-flask.local` (DNS resolves via /etc/hosts)
3. **In CI/CD**: Uses `http://<minikube-ip>` with `Host: hello-flask.local` header

```python
# Pseudo-code of what the test does:
if is_ci_environment():
    url = f"http://{minikube_ip}"
    headers = {"Host": "hello-flask.local"}
else:
    url = "http://hello-flask.local"
    headers = {}

response = requests.get(url, headers=headers)
```

## Verification Commands

```bash
# Test 1: Direct IP (should fail with 404)
curl -v http://$(minikube ip)

# Test 2: IP with Host header (should succeed)
curl -v -H "Host: hello-flask.local" http://$(minikube ip)

# Test 3: Hostname (should succeed if /etc/hosts configured)
curl -v http://hello-flask.local

# Test 4: Check what Ingress is configured for
kubectl get ingress hello-flask-ingress -o yaml | grep -A 5 "rules:"
```

## Key Takeaway

🔑 **Nginx Ingress routing is based on the `Host` HTTP header, not the IP address in the URL!**

- URL: `http://192.168.49.2` → Header: `Host: 192.168.49.2` → 404
- URL: `http://hello-flask.local` → Header: `Host: hello-flask.local` → 200 ✓
- URL: `http://192.168.49.2` + `Host: hello-flask.local` → 200 ✓
