# Educational Tests in CI/CD - Configuration Summary

## Current Behavior

### ✅ Educational Tests **ARE INCLUDED** in CI/CD by Default

The educational tests run automatically in:
- `make k8s-tests`
- `make smoke-test`
- `make test-all`
- GitHub Actions CI/CD pipeline

---

## Why This Configuration?

### **Default Behavior: Include Educational Tests**

**Rationale:**
1. **Comprehensive Validation** - Tests validate real Ingress behavior (routing, consistency, load balancing)
2. **Reasonable Overhead** - Only ~45 seconds extra on a 15-30 minute pipeline
3. **Ensures Tests Stay Working** - Educational tests won't break silently
4. **Demonstrates Full Capabilities** - Shows the repo's complete testing suite

---

## Test Execution Breakdown

### Automated CI/CD Tests (Default)
```bash
pytest test_k8s/ -m "not manual"
```

**Includes:**
- ✅ Basic deployment tests
- ✅ ConfigMap/Secret tests
- ✅ Service tests (NodePort + Ingress)
- ✅ Basic Ingress tests
- ✅ **Educational Ingress tests** (hostname routing, consistency, load balancing)
- ✅ Liveness probe configuration tests

**Excludes:**
- ❌ Manual tests (pod deletion, crash recovery)

**Duration:** ~60-90 seconds

---

### Manual Tests Only
```bash
pytest test_k8s/ -m manual
```

**Includes:**
- 🧪 Pod deletion test (~30s)
- 🧪 Container crash recovery test (~60s)

**Duration:** ~90 seconds

---

### Educational Tests Only
```bash
pytest test_k8s/ -m educational
# OR
make educational-tests
```

**Includes:**
- 📚 Hostname-based routing test (~5s)
- 📚 Response consistency test (~10s)
- 📚 Load balancing test (~30s)

**Duration:** ~45 seconds

---

## Makefile Targets

### New Targets Added:

```bash
# Run only educational tests
make educational-tests

# Run all Ingress tests (basic + educational)
make ingress-tests
```

### Existing Targets (Unchanged):

```bash
# Run k8s tests (includes educational, excludes manual)
make k8s-tests

# Run smoke tests (includes educational, excludes manual)
make smoke-test

# Run all automated tests
make test-all
```

---

## Configuration Files

### `pytest.ini`
```ini
[pytest]
addopts = -v -m "not manual"
markers =
    manual: marks tests as manual-only (not run in automated suite)
    educational: marks tests that demonstrate educational concepts
```

**Key Point:** Educational marker is defined but **NOT excluded** by default.

### Scripts
- `scripts/k8s_tests.sh` - Uses `-m "not manual"` (includes educational)
- `scripts/smoke_test.sh` - Uses `-m "not manual"` (includes educational)

### CI/CD Workflow
- `.github/workflows/ci-cd.yml` - Calls `scripts/k8s_tests.sh` (includes educational)

---

## How to Exclude Educational Tests (If Needed)

If you want to exclude educational tests from CI/CD in the future:

### Option 1: Update `pytest.ini` (Global)
```ini
addopts = -v -m "not manual and not educational"
```

### Option 2: Update Scripts (Per-script)
```bash
# In scripts/k8s_tests.sh and scripts/smoke_test.sh
run_pytest "test_k8s/" "-v -m 'not manual and not educational'"
```

### Option 3: Update CI/CD Workflow (CI-only)
```yaml
- name: Run Kubernetes tests
  run: pytest test_k8s/ -v -m "not manual and not educational"
```

### Option 4: Run Educational Tests Separately
```yaml
# Add a separate CI job for educational tests
- name: Run educational tests
  if: github.event_name == 'push'  # Only on push, not PR
  run: pytest test_k8s/ -m educational -v -s
```

---

## Recommendations

### ✅ **Current Setup is Recommended**

**Keep educational tests in CI/CD because:**

1. **Low Cost** - 45 seconds on a 15-30 minute pipeline is negligible
2. **High Value** - Validates actual Ingress behavior, not just configuration
3. **Prevents Breakage** - Educational tests stay working and up-to-date
4. **Demonstrates Quality** - Shows comprehensive testing practices

### 🎯 **When to Exclude Educational Tests**

Consider excluding if:
- CI/CD pipeline becomes too slow (>30 minutes)
- Running on resource-constrained CI runners
- Tests become flaky in CI environment
- Team prefers to run them manually during development

---

## Test Timing Summary

| Test Suite | Duration | Runs in CI/CD? |
|------------|----------|----------------|
| Unit tests | ~2s | ✅ Yes |
| Basic k8s tests | ~20s | ✅ Yes |
| **Educational tests** | **~45s** | **✅ Yes (current)** |
| Manual tests | ~90s | ❌ No |
| **Total automated** | **~70s** | |
| **Total with manual** | **~160s** | |

---

## Summary

**Current Configuration:**
- ✅ Educational tests run automatically in CI/CD
- ✅ Can be run separately with `make educational-tests`
- ✅ Can be run with all Ingress tests via `make ingress-tests`
- ✅ Easy to exclude later if needed (update pytest.ini)

**Result:** Best of both worlds - comprehensive validation by default with easy opt-out if needed. 🎯
