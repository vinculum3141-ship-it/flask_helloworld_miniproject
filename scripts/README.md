# Scripts Documentation

## Overview

The `scripts/` directory contains modular Bash scripts for automating common development and testing workflows. Each script has a targeted function, making it easy to run only what you need and integrate into CI/CD pipelines.

**Important:** All scripts run within the Minikube environment. Remember to:
- Start Minikube before running scripts: `minikube start`
- Stop Minikube when done: `minikube stop`

---

## Script Reference

### Build & Deployment Scripts

#### `build_image.sh`
**Purpose:** Build the Docker image for the Flask application.

**What it does:**
- Sets up Minikube Docker environment
- Builds Docker image with tag `hello-flask:latest`
- Verifies image was created successfully

**Usage:**
```bash
bash scripts/build_image.sh
```

**When to run:** After making changes to application code or Dockerfile

---

#### `deploy_local.sh`
**Purpose:** Deploy the application to local Kubernetes cluster with Ingress.

**What it does:**
- Sets up Ingress controller (if not already configured)
- Applies Kubernetes manifests (deployment, service, ingress, configmap, secret)
- Waits for pods to become ready
- Displays access information

**Usage:**
```bash
bash scripts/deploy_local.sh
```

**When to run:** After building the image, to deploy to Minikube

**Note:** This deploys with Ingress (ClusterIP service). For NodePort deployment, apply manifests manually.

---

#### `delete_local.sh`
**Purpose:** Clean up all Kubernetes resources.

**What it does:**
- Deletes all application resources (deployment, service, ingress, configmap, secret)
- Confirms cleanup was successful

**Usage:**
```bash
bash scripts/delete_local.sh
```

**When to run:** When you need to clean up resources or start fresh

---

### Testing Scripts

#### `unit_tests.sh`
**Purpose:** Run application-level unit tests.

**What it does:**
- Runs pytest on `app/tests/` directory
- Tests Flask application logic independently of Kubernetes

**Usage:**
```bash
bash scripts/unit_tests.sh
```

**Duration:** Fast (~1-2 seconds)

---

#### `k8s_tests.sh`
**Purpose:** Run Kubernetes integration tests (automated suite only).

**What it does:**
- Runs pytest on `test_k8s/` directory
- Excludes manual tests using `-m 'not manual'` marker
- Tests deployment, services, ingress, probes, configmaps

**Usage:**
```bash
bash scripts/k8s_tests.sh
```

**Duration:** ~15-20 seconds

**Note:** Excludes manual tests (pod deletion, crash recovery) for faster feedback

---

#### `liveness_test.sh`
**Purpose:** Run liveness probe and self-healing tests with multiple modes.

**What it does:**
- **Default mode:** Runs automated liveness probe configuration tests
- **Manual mode:** Runs behavioral tests (pod deletion, crash recovery)
- **Config mode:** Runs only configuration checks

**Usage:**
```bash
# Automated configuration tests only (default)
bash scripts/liveness_test.sh

# Manual behavioral tests (pod deletion, crash recovery)
bash scripts/liveness_test.sh --manual

# Configuration check only
bash scripts/liveness_test.sh --config
```

**Duration:**
- Automated/Config: Fast (~2-3 seconds)
- Manual: Slow (~60-90 seconds)

**Note:** Manual tests involve wait times and are best run explicitly

---

#### `smoke_test.sh`
**Purpose:** Quick validation of all critical functionality (automated tests only).

**What it does:**
- Runs all automated Kubernetes tests
- Excludes manual tests using `-m 'not manual'` marker
- Provides fast feedback on deployment health

**Usage:**
```bash
bash scripts/smoke_test.sh
```

**Duration:** ~15-20 seconds

**When to run:** After deployment to quickly verify everything works

---

### Utility Scripts

#### `port_forward.sh`
**Purpose:** Forward service port to localhost for local testing.

**What it does:**
- Sets up port forwarding from localhost:8080 to service port 5000
- Keeps running until interrupted (Ctrl+C)
- Displays access URL

**Usage:**
```bash
bash scripts/port_forward.sh
# Then access: http://localhost:8080
```

**When to run:** When you need to test the service directly without Ingress/NodePort

**Note:** Blocks terminal - use Ctrl+C to stop

---

#### `minikube_service_url.sh`
**Purpose:** Get service URL and access methods.

**What it does:**
- Auto-detects service type (NodePort or ClusterIP)
- Provides appropriate access instructions and tests connectivity
- For NodePort: Shows `minikube service` URL and tests the service
- For ClusterIP+Ingress: Shows multiple access methods (hostname, IP+Host header, port-forward)
- Tests connectivity intelligently (tries hostname first, falls back to IP if needed)

**Usage:**
```bash
bash scripts/minikube_service_url.sh
# or
make minikube-url
```

**Output examples:**

For ClusterIP with Ingress:
```
[INFO] Service type: ClusterIP
[INFO] Ingress hostname: hello-flask.local
Access via: http://hello-flask.local
  or: curl -H "Host: hello-flask.local" http://192.168.49.2
[SUCCESS] App is accessible
```

For NodePort:
```
[INFO] Service type: NodePort
[INFO] Access your app at: http://192.168.49.2:30123
```

**When to run:** When you need to know how to access the deployed service
```bash
bash scripts/minikube_service_url.sh
```

**When to run:** When you need to know how to access the deployed service

---

#### `setup_ingress.sh`
**Purpose:** Set up Ingress controller and configure host resolution.

**What it does:**
- Enables nginx ingress controller in Minikube
- Waits for ingress controller pods to be ready
- Adds `hello-flask.local` entry to `/etc/hosts`
- Verifies setup is complete

**Usage:**
```bash
bash scripts/setup_ingress.sh
```

**When to run:** Once per Minikube cluster, before deploying with Ingress

**Note:** Requires sudo for `/etc/hosts` modification

---

## Quick Reference Table

| Script | Purpose | Duration | Blocks Terminal |
|--------|---------|----------|-----------------|
| `build_image.sh` | Build Docker image | ~10-20s | No |
| `deploy_local.sh` | Deploy to Minikube | ~15-30s | No |
| `delete_local.sh` | Cleanup resources | ~5s | No |
| `unit_tests.sh` | App unit tests | ~2s | No |
| `k8s_tests.sh` | K8s integration tests | ~15-20s | No |
| `liveness_test.sh` | Liveness/probe tests | ~2-90s* | No |
| `smoke_test.sh` | Quick validation | ~15-20s | No |
| `port_forward.sh` | Port forwarding | Continuous | Yes |
| `minikube_service_url.sh` | Get access URL | ~1s | No |
| `setup_ingress.sh` | Setup Ingress | ~30-60s | No |

\* *Duration depends on mode: config (~2s), automated (~3s), manual (~60-90s)*

---

## Scripts Architecture

All bash scripts use a **shared utilities library** for consistent output and easier maintenance.

### Shared Library (`scripts/lib/common.sh`)

**Location:** `scripts/lib/common.sh`

**Features:**
- **Color definitions**: `GREEN`, `BLUE`, `YELLOW`, `RED`, `NC` (No Color)
- **Logging functions**: 
  - `log_info()` - Informational messages (blue)
  - `log_success()` - Success messages (green)
  - `log_warning()` - Warning messages (yellow)
  - `log_error()` - Error messages (red)
  - `log_note()` - Important notes (yellow)
- **Header formatting**: `print_header()` - Consistent script headers
- **Pytest helpers**: `run_pytest()` - Standardized test execution
- **Validation helpers**: 
  - `command_exists()` - Check if command is available
  - `check_git_repo()` - Verify we're in a git repository
- **Path helpers**: 
  - `get_scripts_dir()` - Get scripts directory path
  - `get_project_root()` - Get project root path

### Benefits

✅ **Single source of truth** - Colors and formatting defined once  
✅ **Consistent output** - All scripts use the same style  
✅ **Easier maintenance** - Update logging in one place, applies everywhere  
✅ **Better error handling** - Standardized error messages and exit codes  
✅ **Code reuse** - Common patterns extracted into reusable functions  

### Usage Pattern

All scripts follow this pattern:

```bash
#!/bin/bash

# Source the common library
source "$(dirname "$0")/lib/common.sh"

# Print script header
print_header "My Script Title"

# Use logging functions
log_info "Processing started..."

# Check prerequisites
if ! command_exists kubectl; then
    log_error "kubectl is not installed"
    exit 1
fi

# Run pytest with standard helper
run_pytest "test_k8s/" "-v"

# Success message
log_success "All done!"
```

### Example Output

When you run a script, you'll see consistent, color-coded output:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  My Script Title
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ Processing started...
✓ All done!
```

---

## Makefile Integration

All scripts can also be run via Makefile targets for convenience. The Makefile provides shortcuts that are easier to remember and type.

### Quick Help

To see all available Makefile targets at any time:
```bash
make help
```

### Build & Deployment Targets

```bash
make build           # Build Docker image (runs build_image.sh)
make deploy          # Deploy to local cluster (runs deploy_local.sh)
make delete          # Delete local deployment (runs delete_local.sh)
```

### Testing Targets

**Individual Test Targets:**
```bash
make unit-tests      # Run unit tests (runs unit_tests.sh)
make k8s-tests       # Run K8s integration tests (runs k8s_tests.sh)
make smoke-test      # Run smoke tests - quick validation (runs smoke_test.sh)
```

**Liveness Test Variations:**
```bash
make liveness-test         # Run automated liveness probe configuration tests
make liveness-test-manual  # Run manual behavioral tests (pod deletion, crash recovery)
make liveness-test-config  # Run only liveness probe configuration check
```

**Composite Test Targets:**
```bash
make test-all        # Run all tests (unit + k8s integration)
```

### Utility Targets

```bash
make port-forward    # Forward service port to localhost (runs port_forward.sh)
make minikube-url    # Get service URL and access methods (runs minikube_service_url.sh)
```

### Validation Targets

**Pre-Push Validation:**
```bash
make validate-repo      # Validate repository structure (runs validate_repo_structure.sh)
make validate-workflow  # Validate GitHub Actions workflow (runs validate_workflow.sh)
make validate-all       # Run all validation checks (both scripts)
```

See [Development Workflow](../docs/DEVELOPMENT_WORKFLOW.md) for detailed validation documentation.

### Changelog Targets

```bash
make changelog                              # Generate changelog from all commits
make changelog-since TAG=v1.0.0             # Generate changelog since specific tag
make changelog-range FROM=v1.0.0 TO=v2.0.0  # Generate changelog between tags
make changelog-dev                          # Append auto-generated changelog to CHANGELOG_DEV.md
make changelog-dev-since TAG=v1.0.0         # Append changelog since tag to CHANGELOG_DEV.md
```

### Composite Workflow Targets

These targets run multiple steps in sequence:

```bash
make full-deploy     # Complete workflow: build → deploy → smoke test
make test-all        # Run both unit and k8s tests
```

### Complete Makefile Reference

| Target | Script/Action | Description |
|--------|---------------|-------------|
| `build` | `build_image.sh` | Build Docker image |
| `deploy` | `deploy_local.sh` | Deploy to local cluster |
| `delete` | `delete_local.sh` | Delete local deployment |
| `unit-tests` | `unit_tests.sh` | Run unit tests |
| `k8s-tests` | `k8s_tests.sh` | Run K8s integration tests |
| `liveness-test` | `liveness_test.sh` | Run automated liveness tests |
| `liveness-test-manual` | `liveness_test.sh --manual` | Run manual behavioral tests |
| `liveness-test-config` | `liveness_test.sh --config` | Run config check only |
| `smoke-test` | `smoke_test.sh` | Run smoke tests |
| `port-forward` | `port_forward.sh` | Forward service port |
| `minikube-url` | `minikube_service_url.sh` | Get service URL |
| `validate-repo` | `validate_repo_structure.sh` | Validate repository structure |
| `validate-workflow` | `validate_workflow.sh` | Validate GitHub Actions workflow |
| `validate-all` | Composite | Run all validation checks |
| `changelog` | `generate_changelog.sh` | Generate changelog |
| `test-all` | Composite | Run unit + k8s tests |
| `full-deploy` | Composite | Build + deploy + smoke test |
| `help` | Display help | Show all available targets |

### Benefits of Using Makefile

✅ **Shorter commands** - `make test-all` vs `bash scripts/unit_tests.sh && bash scripts/k8s_tests.sh`  
✅ **Easier to remember** - Standard make targets like `build`, `deploy`, `test`  
✅ **Composable** - Combine multiple steps with composite targets  
✅ **Auto-completion** - Many shells support make target auto-completion  
✅ **Self-documenting** - `make help` shows all available commands  

### Usage Examples

**Quick deployment:**
```bash
make full-deploy
# Equivalent to:
# bash scripts/build_image.sh
# bash scripts/deploy_local.sh
# bash scripts/smoke_test.sh
```

**Run all tests:**
```bash
make test-all
# Equivalent to:
# bash scripts/unit_tests.sh
# bash scripts/k8s_tests.sh
```

**Check available commands:**
```bash
make help
```

---

## Workflow Examples

### Complete Deployment Workflow

```bash
# 1. Start Minikube
minikube start

# 2. Setup Ingress (one time)
bash scripts/setup_ingress.sh

# 3. Build and deploy
bash scripts/build_image.sh
bash scripts/deploy_local.sh

# 4. Verify deployment
bash scripts/smoke_test.sh

# 5. Get access URL
bash scripts/minikube_service_url.sh

# 6. Cleanup when done
bash scripts/delete_local.sh
minikube stop
```

### Testing Workflow

```bash
# Run unit tests
bash scripts/unit_tests.sh

# Run all K8s tests (automated)
bash scripts/k8s_tests.sh

# Run manual tests if needed
bash scripts/liveness_test.sh --manual

# Quick smoke test
bash scripts/smoke_test.sh
```

### Development Workflow

```bash
# Make code changes...

# Rebuild and redeploy
bash scripts/build_image.sh
bash scripts/delete_local.sh
bash scripts/deploy_local.sh

# Test changes
bash scripts/smoke_test.sh
```

---

## Troubleshooting

### Script Fails with "command not found"

**Problem:** Script can't find `kubectl`, `minikube`, or other commands

**Solution:**
```bash
# Check prerequisites
kubectl version --client
minikube version
docker --version

# Install missing tools
# See main README.md for installation instructions
```

### Tests Fail - Pods Not Ready

**Problem:** Tests run before pods are ready

**Solution:**
```bash
# Wait for pods manually
kubectl wait --for=condition=ready pod -l app=hello-flask --timeout=60s

# Then run tests
bash scripts/k8s_tests.sh
```

### Port Forwarding Conflicts

**Problem:** Port 8080 already in use

**Solution:**
```bash
# Find and kill process using port 8080
lsof -ti:8080 | xargs kill -9

# Or use a different port
kubectl port-forward svc/hello-flask 8081:5000
```

### Ingress Not Working

**Problem:** Can't access via `hello-flask.local`

**Solution:**
```bash
# Re-run ingress setup
bash scripts/setup_ingress.sh

# Verify /etc/hosts entry
grep hello-flask /etc/hosts

# Check ingress controller
kubectl get pods -n ingress-nginx
```

---

## Contributing

When adding new scripts:

1. **Source the common library:**
   ```bash
   source "$(dirname "$0")/lib/common.sh"
   ```

2. **Use standard logging functions:**
   - `log_info()` for informational messages
   - `log_success()` for success
   - `log_error()` for errors
   - `log_warning()` for warnings

3. **Add to this README** with:
   - Purpose description
   - What it does
   - Usage example
   - When to run it
   - Special notes

4. **Add Makefile target** (optional but recommended)

5. **Test thoroughly** before committing

---

## Related Documentation

- **[Main README](../README.md)** - Project overview and quick start
- **[Test README](../test_k8s/README.md)** - Test suite documentation
- **[Script Updates](../docs/scripts/SCRIPT_UPDATES.md)** - Recent script changes
- **[Documentation Index](../docs/README.md)** - Complete documentation hub
