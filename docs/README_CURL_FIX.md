# README curl Commands Fixed

## Changes Made

Updated all `curl` examples in the documentation to use the correct `Host` header when accessing Minikube IP directly.

## Why This Was Needed

When using Ingress with a hostname rule, direct access via IP fails:

```bash
# ❌ WRONG (returns 404):
curl http://$(minikube ip)

# ✅ CORRECT (returns 200):
curl -H "Host: hello-flask.local" http://$(minikube ip)
```

## Files Updated

### 1. README.md
**Section: "Manual verification"**
```bash
# Before (incorrect):
curl http://$(minikube ip)

# After (correct):
curl -H "Host: hello-flask.local" http://$(minikube ip)
# Or use hostname if /etc/hosts is configured
curl http://hello-flask.local
```

**Section: "Running specific tests"**
- Added example for simulating CI environment: `CI=true pytest ...`
- Added note explaining automatic environment detection

### 2. docs/CI_CD_FIX_SUMMARY.md
**Section: "Additional Debugging"**
```bash
# Before (incorrect):
curl http://$(minikube ip)

# After (correct):
curl -H "Host: hello-flask.local" http://$(minikube ip)
# Or use hostname if /etc/hosts is configured:
curl http://hello-flask.local
```

## Quick Reference

### For Local Testing

**Option 1: Use hostname (easiest)**
```bash
# Requires /etc/hosts configured (run scripts/setup_ingress.sh)
curl http://hello-flask.local
```

**Option 2: Use IP with Host header**
```bash
# Works without /etc/hosts
curl -H "Host: hello-flask.local" http://$(minikube ip)
```

**Option 3: Port-forward (bypasses Ingress)**
```bash
kubectl port-forward svc/hello-flask 5000:5000
curl http://localhost:5000
```

### For Testing in CI Mode Locally

```bash
# Simulate CI/CD environment
CI=true pytest test_k8s/test_service_access.py -v -s

# Output will show:
# "Detected CI environment - using Minikube IP instead of hostname"
# "Using Minikube IP: 192.168.49.2 with Host header: hello-flask.local"
```

### Verification

Test both methods work:
```bash
# Method 1: Hostname
curl http://hello-flask.local
# {"message":"Hello from Flask on Kubernetes (Minikube)!"}

# Method 2: IP + Host header
curl -H "Host: hello-flask.local" http://$(minikube ip)
# {"message":"Hello from Flask on Kubernetes (Minikube)!"}
```

## Summary

All documentation now correctly shows that when accessing Ingress via Minikube IP, you must include the `Host` header that matches the Ingress rule. This is how nginx-ingress routing works!

✅ README.md updated
✅ docs/CI_CD_FIX_SUMMARY.md updated
✅ All curl examples now work correctly
✅ Added CI simulation example for tests
