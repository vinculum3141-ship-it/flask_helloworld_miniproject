# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Ingress Support (November 2025)

#### Infrastructure
- **Ingress resource** (`k8s/ingress.yaml`)
  - Support for nginx ingress controller (Minikube)
  - Support for AWS Load Balancer Controller (EKS)
  - Uses modern `spec.ingressClassName` instead of deprecated annotation
  - Host-based routing configuration for `hello-flask.local`
  - Comprehensive annotations for both Minikube and EKS deployments

#### Scripts
- **`scripts/setup_ingress.sh`** - Automated Ingress setup for Minikube
  - Enables nginx ingress addon
  - Waits for ingress controller readiness
  - Configures `/etc/hosts` with user confirmation
  - Provides next steps guidance

#### Tests
- **`test_k8s/test_ingress.py`** - Dedicated Ingress validation tests
  - `test_ingress_exists()` - Verifies Ingress resource deployment
  - `test_ingress_has_rules()` - Validates routing rules
  - `test_ingress_has_address()` - Checks address assignment
  - `test_ingress_class()` - Verifies ingress class configuration
  - Auto-skips when Ingress not deployed

#### Documentation
- **`docs/INGRESS_404_EXPLAINED.md`** - Visual guide explaining nginx routing and Host headers
- **`docs/CI_CD_FIX_SUMMARY.md`** - CI/CD test fixes and Host header handling
- **`docs/DEBUGGING_CI_CD.md`** - Comprehensive debugging guide for pipeline issues
- **`docs/README_CURL_FIX.md`** - Documentation fixes for curl commands
- **`docs/MINIKUBE_SERVICE_URL_FIX.md`** - Script update documentation

### Changed

#### Service Configuration
- **`k8s/service.yaml`** - Changed from `NodePort` to `ClusterIP`
  - Required for Ingress compatibility
  - Added documentation on how to switch back to NodePort
  - Maintains backward compatibility instructions

#### CI/CD Workflow
- **`.github/workflows/ci-cd.yml`**
  - Added Ingress controller enablement step
  - Added wait for Ingress readiness
  - Added debug deployment state step (shows Minikube IP, services, ingresses, logs)
  - Updated deployment step documentation to mention Ingress

#### Deployment Scripts
- **`scripts/deploy_local.sh`**
  - Now deploys `k8s/ingress.yaml` automatically
  - Maintains same deployment workflow

- **`scripts/minikube_service_url.sh`** - Complete rewrite
  - Auto-detects service type (NodePort or ClusterIP)
  - Shows multiple access methods for Ingress
  - Smart connectivity testing (hostname fallback to IP + Host header)
  - Helpful error messages and guidance
  - Backward compatible with NodePort

- **`scripts/port_forward.sh`**
  - Updated to detect and report service type
  - Works with both NodePort and ClusterIP
  - Enhanced user feedback

#### Tests
- **`test_k8s/test_service_access.py`** - Major update for Ingress compatibility
  - Auto-detects service type (NodePort or ClusterIP)
  - CI/CD environment detection (`CI=true` or `GITHUB_ACTIONS=true`)
  - Sends correct `Host` header when using Minikube IP
  - Smart URL selection: hostname (local) vs IP (CI)
  - Enhanced debug output showing which URL and headers are used
  - Comprehensive error messages

#### Documentation
- **`README.md`**
  - Added "Deploy the app to Kubernetes" section with two options:
    - Option A: Direct Access (without Ingress/NodePort)
    - Option B: Using Ingress (production-like setup)
  - Added Ingress setup instructions
  - Updated test documentation showing both deployment methods work
  - Added Troubleshooting section for local testing and CI/CD issues
  - Updated "Deploying to AWS EKS" section with Ingress configuration
  - Added Minikube vs EKS comparison table
  - Updated script descriptions to mention Ingress support
  - Fixed curl examples to use correct Host header
  - Added CI simulation example for tests
  - Updated prerequisites with clearer package installation

- **`Makefile`**
  - Updated help text for `minikube-url` target
  - Maintained all existing targets

### Fixed

#### Ingress Deprecation Warning
- Updated `k8s/ingress.yaml` to use `spec.ingressClassName: nginx` instead of deprecated `kubernetes.io/ingress.class` annotation
- Applied to both Minikube (nginx) and EKS (alb) configurations

#### 404 Errors with Ingress
- **Root cause**: Nginx Ingress routes based on `Host` HTTP header, not IP address
- **Solution**: Tests and scripts now send `Host: hello-flask.local` header when accessing via Minikube IP
- All curl examples in documentation updated to show correct usage

#### CI/CD Pipeline Failures
- **Root cause**: `http://hello-flask.local` hostname doesn't resolve in GitHub Actions (no `/etc/hosts`)
- **Solution**: Tests auto-detect CI environment and use Minikube IP with correct Host header
- Added comprehensive debugging output in workflow

#### Script Failures
- **`scripts/minikube_service_url.sh`**: Failed with ClusterIP service (expected NodePort)
- **Solution**: Complete rewrite to support both service types intelligently

### Removed

- **`setup_env.sh`** (recommended for removal)
  - Contains incorrect paths from different project
  - Not referenced anywhere in codebase
  - Functionality covered in README

## Testing

All changes maintain backward compatibility:

### With Ingress (ClusterIP Service)
```bash
# Local development
curl http://hello-flask.local
pytest test_k8s/ -v  # All tests pass

# CI/CD simulation
CI=true pytest test_k8s/ -v  # Uses Minikube IP + Host header
```

### With NodePort (without Ingress)
```bash
# Change service type in k8s/service.yaml to NodePort
minikube service hello-flask --url
pytest test_k8s/ -v  # All tests still pass
```

## Migration Guide

### For Existing Deployments

If you have an existing deployment without Ingress:

1. **One-time setup** (local development):
   ```bash
   bash scripts/setup_ingress.sh
   ```

2. **Deploy with Ingress**:
   ```bash
   kubectl apply -f k8s/ingress.yaml
   ```

3. **Access the app**:
   ```bash
   curl http://hello-flask.local
   ```

### To Revert to NodePort

1. Edit `k8s/service.yaml`:
   ```yaml
   spec:
     type: NodePort  # Change from ClusterIP
   ```

2. Remove Ingress (optional):
   ```bash
   kubectl delete -f k8s/ingress.yaml
   ```

3. Access via NodePort:
   ```bash
   minikube service hello-flask --url
   ```

## Summary Statistics

- **Files Added**: 8 (1 Ingress manifest, 1 script, 5 docs, 1 test file)
- **Files Modified**: 9 (service, deployment script, CI/CD workflow, tests, README, Makefile, etc.)
- **Files Recommended for Removal**: 1 (setup_env.sh)
- **Tests Added**: 4 new test functions
- **Tests Modified**: 1 major update (test_service_access.py)
- **Documentation Pages**: 5 new comprehensive guides

## Compatibility

- ✅ Kubernetes 1.18+ (for `spec.ingressClassName` support)
- ✅ Minikube with nginx ingress addon
- ✅ AWS EKS with AWS Load Balancer Controller
- ✅ Python 3.11+
- ✅ pytest 9.0+
- ✅ requests library

## Contributors

This release includes comprehensive Ingress support for both local (Minikube) and production (EKS) environments, with intelligent fallbacks, extensive testing, and thorough documentation.

---

## Template for Future Updates

```markdown
## [Version] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security updates
```
