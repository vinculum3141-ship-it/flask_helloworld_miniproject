# Bash Script Updates for Test Refactoring

## Summary

The bash scripts have been updated to accommodate the Python test refactoring, particularly to properly handle the new pytest markers and split test files.

---

## Changes Made

### 1. **scripts/k8s_tests.sh** ✅

**Changed:**
```bash
# Before:
run_pytest "test_k8s/" "-v"

# After:
run_pytest "test_k8s/" "-v -m 'not manual'"
```

**Impact:**
- Now explicitly excludes tests marked with `@pytest.mark.manual`
- Prevents slow, timing-dependent tests from running in CI/CD
- Updated log message to reflect manual test exclusion

**Usage:**
```bash
make k8s-tests  # Runs all tests except manual ones
```

---

### 2. **scripts/smoke_test.sh** ✅

**Changed:**
```bash
# Before:
run_pytest "test_k8s/" "-v"
# Note about test_crash_recovery_manual.py

# After:
run_pytest "test_k8s/" "-v -m 'not manual'"
# Updated note about using pytest markers
```

**Impact:**
- Explicitly excludes `@pytest.mark.manual` tests
- Smoke tests now only run fast configuration checks
- Better guidance on running manual tests

**Usage:**
```bash
make smoke-test  # Quick validation without manual tests
```

---

### 3. **scripts/port_forward.sh** ✅

**Changed:**
```bash
# Before:
# CI coverage: Service reachability is validated in pytest via
#   test_k8s/test_service_access.py

# After:
# CI coverage: Service reachability is validated in pytest via
#   test_k8s/test_service_nodeport.py (NodePort service type)
#   test_k8s/test_service_ingress.py (ClusterIP with Ingress)
```

**Impact:**
- Documentation updated to reference new split test files
- Clearer indication of which tests cover which scenarios

**Usage:**
```bash
bash scripts/port_forward.sh  # Still works the same
```

---

### 4. **scripts/minikube_service_url.sh** ✅

**Changed:**
```bash
# Before:
# In CI, this functionality is tested via pytest:
#   - See: `test_k8s/test_service_access.py`

# After:
# In CI, this functionality is tested via pytest:
#   - See: `test_k8s/test_service_nodeport.py` (NodePort tests)
#   - See: `test_k8s/test_service_ingress.py` (Ingress tests)
```

**Impact:**
- Documentation updated to reference new split test files
- Better clarity on test coverage

**Usage:**
```bash
bash scripts/minikube_service_url.sh  # Still works the same
```

---

### 5. **scripts/liveness_test.sh** ✅ (Already Compatible)

**No changes needed** - This script was already designed to work with pytest markers:
```bash
# Already uses:
run_pytest "test_k8s/" "-v -s -m manual"  # For manual tests
run_pytest "test_k8s/test_liveness_probe.py" "-v -s"  # For config tests
```

**Usage:**
```bash
make liveness-test         # Config tests only (fast)
make liveness-test-manual  # Manual behavioral tests (slow)
```

---

## Pytest Marker Strategy

### Marker Usage in Scripts

| Script | Marker Filter | Tests Run |
|--------|--------------|-----------|
| `k8s_tests.sh` | `-m 'not manual'` | All except manual |
| `smoke_test.sh` | `-m 'not manual'` | All except manual |
| `liveness_test.sh` | `-m manual` (with flag) | Only manual tests |
| No marker | (all tests) | Everything |

### Available Markers

From `test_k8s/conftest.py`:
- `@pytest.mark.manual` - Timing-dependent tests (excluded from CI)
- `@pytest.mark.slow` - Tests that take longer
- `@pytest.mark.ingress` - Requires Ingress controller
- `@pytest.mark.nodeport` - Requires NodePort service type

---

## Testing the Updates

### Verify Script Changes Work

```bash
# Test k8s_tests.sh excludes manual tests
bash scripts/k8s_tests.sh
# Should NOT run test_crash_recovery_manual.py tests

# Test smoke_test.sh excludes manual tests
bash scripts/smoke_test.sh
# Should be fast, no manual tests

# Test liveness_test.sh manual option
bash scripts/liveness_test.sh --manual
# Should run manual tests explicitly
```

### Run Manual Tests Explicitly

```bash
# Run manual tests directly
pytest test_k8s/ -v -m manual

# Or use the liveness script
bash scripts/liveness_test.sh --manual
```

---

## Benefits

✅ **CI/CD Optimization**: Automated test runs skip slow, flaky manual tests  
✅ **Clear Documentation**: Script comments point to correct test files  
✅ **Backward Compatible**: Existing Makefile targets still work  
✅ **Flexible Testing**: Easy to run different test subsets  
✅ **Better Organization**: Markers make test categorization explicit  

---

## Backward Compatibility

All existing Makefile targets continue to work:

```bash
make k8s-tests          # ✅ Now excludes manual tests
make smoke-test         # ✅ Now excludes manual tests  
make liveness-test      # ✅ Works as before
make liveness-test-manual  # ✅ Works as before
```

---

## Migration Notes

If you have custom scripts that call pytest directly on `test_k8s/`:

**Before:**
```bash
pytest test_k8s/ -v
```

**After (recommended for CI):**
```bash
pytest test_k8s/ -v -m 'not manual'  # Exclude slow tests
```

**After (comprehensive testing):**
```bash
pytest test_k8s/ -v  # Run everything including manual
```

---

## Related Documentation

- See `test_k8s/README.md` for test usage examples
- See `test_k8s/REFACTORING_SUMMARY.md` for Python refactoring details
- See `test_k8s/conftest.py` for marker definitions
