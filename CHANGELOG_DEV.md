# Development Changelog

> **Purpose**: Track development changes, refactorings, and improvements not captured in production releases.  
> **Audience**: Developers working on this project.  
> **Format**: Manual entries for significant work; auto-generated entries archived at bottom.

---

## [Unreleased] - 2025-11-22

### Script Refactoring - Phase 3 (Advanced Improvements)

**Context**: Further improve code quality by removing fragile `eval` usage and adding performance tracking.

**Changed**:
- **scripts/lib/common.sh**: Improved pytest argument handling
  - Removed `eval` from `run_pytest()` function
  - Removed `eval` from `run_pytest_optional()` function
  - Replaced with array-based argument handling: `eval "args_array=($pytest_args)"`
  - Better handling of complex pytest marker expressions (e.g., `-m 'not manual and not nodeport'`)
  - More secure and maintainable approach

- **scripts/lib/common.sh**: Added execution timing wrapper
  - New `time_command()` function for performance tracking
  - Logs start time, runs command, logs completion with duration
  - Useful for identifying slow operations in scripts
  - Example: `time_command "Building image" docker build -t myapp .`

**Testing**:
- ✅ make unit-tests: 22 tests passed
- ✅ make smoke-test: 31 tests passed, 1 skipped
- ✅ bash scripts/health_endpoint_tests.sh: 7 tests passed
- ✅ bash scripts/readiness_test.sh --manual: Correctly handles exit code 5
- ✅ make validate-all: All checks passed

**Impact**:
- **Security**: Eliminated `eval` which can be dangerous with untrusted input
- **Reliability**: Better argument handling prevents parsing errors
- **Performance Visibility**: New timing wrapper helps identify bottlenecks
- **Maintainability**: Cleaner, more understandable code

**Related**: Completes Phase 3 of SCRIPT_REFACTORING_ANALYSIS.md

---

### Health Test Timing Improvements

**Context**: Intermittent smoke-test failures after running health-endpoint tests due to insufficient wait time for service restoration.

**Changed**:
- **scripts/health_endpoint_tests.sh**: Increased wait times in restore_service()
  - Service stabilization: 3s → 5s (after switching back to ClusterIP)
  - Added ingress controller update wait: +3s new wait
  - Total restoration wait: 3s → 8s
  - Ensures ingress controller fully recognizes service type changes

**Testing**:
- ✅ health_endpoint_tests.sh: 7 tests passed
- ✅ smoke-test immediately after: 31 tests passed, 1 skipped
- ✅ validate-all: All checks passed

**Impact**:
- **Reliability**: Eliminates intermittent smoke-test failures after health tests
- **Stability**: Gives ingress controller adequate time to update routing
- **CI/CD**: More robust test sequencing in automated pipelines

---

### Script Refactoring - Phase 1 (Maintainability & Debugging)

**Context**: Scripts had code duplication, inconsistent error handling, and no debug mode.

**Changed**:
- **build_image.sh**: Refactored to use common.sh library
  - Removed duplicate color definitions (10 lines)
  - Removed duplicate print_header function (5 lines)
  - Added `set -euo pipefail` for strict error handling
  - Converted to use log_info(), log_note(), log_success()
  - Net reduction: ~10 lines, better consistency

- **lib/common.sh**: Added debug mode support
  - New `enable_debug_mode()` function
  - Checks DEBUG or VERBOSE environment variables
  - Enables `set -x` for trace output when DEBUG=1
  - Usage: `DEBUG=1 bash scripts/liveness_test.sh`

- **Error handling standardized** across 9 scripts:
  - Changed from `set -e` to `set -euo pipefail`
  - Scripts updated: liveness_test.sh, readiness_test.sh, health_endpoint_tests.sh, smoke_test.sh, k8s_tests.sh, unit_tests.sh, build_image.sh, validate_repo_structure.sh, deploy_local.sh
  - Benefits: Catch undefined variables, pipeline errors, stricter failure modes

**Testing**:
- ✅ unit_tests.sh: 22 tests passed
- ✅ smoke_test.sh: 31 tests passed, 1 skipped
- ✅ Debug mode verified with DEBUG=1

**Impact**:
- **Maintainability**: Single source of truth for logging functions
- **Debugging**: Easy verbose mode for troubleshooting (DEBUG=1)
- **Reliability**: Stricter error handling prevents silent failures
- **Consistency**: All scripts follow same patterns

**Related**: See SCRIPT_REFACTORING_ANALYSIS.md for full analysis and Phase 2 recommendations

### Documentation Updates - Phase 1 Refactoring

**Context**: Updated documentation to reflect Phase 1 script refactoring changes.

**Changed**:
- **scripts/README.md**:
  - Added `enable_debug_mode()` to shared library features list
  - Updated Benefits section to mention strict error handling (`set -euo pipefail`)
  - Added new "Debug Mode" section with usage examples and when to use
  - Added "Script Debugging" to Troubleshooting section as first troubleshooting item
  - Documents DEBUG=1 and VERBOSE=1 environment variables

- **docs/development/DEVELOPMENT_WORKFLOW.md**:
  - Added "Script Debugging" as first troubleshooting item
  - Documents how to use DEBUG=1 with validation scripts
  - Explains what debug output shows and when to use it

**Impact**:
- **Discoverability**: Users can easily find debug mode feature
- **Troubleshooting**: Debug mode now first suggestion for script issues
- **Completeness**: All Phase 1 features fully documented

### Bug Fix - Arithmetic Expression in set -e Mode

**Context**: After adding `set -euo pipefail` to scripts, `validate_repo_structure.sh` was exiting prematurely when encountering warnings.

**Problem**: 
- Arithmetic expressions like `((WARNINGS++))` return 0 when incrementing from 0
- Under `set -e`, a return value of 0 causes immediate script exit
- Script would fail during `warn_if_missing()` calls before reaching validation summary

**Fixed**:
- Changed `((ERRORS++))` to `ERRORS=$((ERRORS + 1))` (3 instances)
- Changed `((WARNINGS++))` to `WARNINGS=$((WARNINGS + 1))` (2 instances)
- New syntax always returns success (non-zero) regardless of arithmetic result

**Testing**:
- ✅ Script now completes with warnings (exit code 0)
- ✅ Script shows full validation summary
- ✅ `make release-prep` now proceeds past validation step

**Impact**:
- **Reliability**: Scripts with counters work correctly under strict mode
- **Usability**: Validation scripts provide complete output before exiting
- **CI/CD**: Release preparation workflow no longer blocked by warnings

### Bug Fix - Health Tests Timing Issue

**Context**: Running `make health-tests` followed immediately by `make smoke-test` would sometimes fail because pods/service weren't fully stabilized.

**Problem**:
- `health_endpoint_tests.sh` restores service from NodePort to ClusterIP at exit
- One health test triggers `kubectl rollout restart` to test health during pod restart
- Script didn't wait for service or pods to stabilize after restoration
- Subsequent tests could start before pods were ready or service endpoints updated

**Fixed** (`scripts/health_endpoint_tests.sh`):
- Added 3-second sleep after patching service back to ClusterIP
- Added `kubectl wait --for=condition=ready` to ensure all pods ready
- Service restoration now fully completes before script exits

**Testing**:
- ✅ `make health-tests && make smoke-test` now works reliably
- ✅ No more intermittent failures when tests run in sequence
- ✅ Service fully stabilized before next test suite begins

**Impact**:
- **Reliability**: Test workflows can run back-to-back without failures
- **CI/CD**: Release preparation workflow (`make release-prep`) more stable
- **Developer Experience**: Less confusion from flaky test failures

### Script Refactoring - Phase 2 (Improved Abstractions)

**Context**: Extract common patterns into reusable helper functions for better code reuse.

**Added to lib/common.sh**:
- **run_pytest_optional()**: Handle pytest exit code 5 (no tests collected) gracefully
  - Simplifies scripts that run optional/manual tests
  - Automatically treats "no tests found" as success
  - Custom warning messages for different contexts
  - Usage: `run_pytest_optional "test_k8s/" "-v -m manual -k readiness" "Running optional tests"`

- **kubectl_safe()**: Wrapper for kubectl with better error context
  - Logs the operation being performed
  - Provides detailed error messages on failure
  - Consistent kubectl error handling across scripts
  - Usage: `kubectl_safe "Applying deployment" apply -f k8s/deployment.yaml`

- **wait_for_pods_ready()**: Common pod readiness wait pattern
  - Standardized way to wait for pods
  - Configurable timeout (default 60s)
  - Clean success/warning messages
  - Usage: `wait_for_pods_ready "app=hello-flask" 60`

**Refactored Scripts**:
- **readiness_test.sh**: Simplified using `run_pytest_optional()`
  - Removed 18 lines of manual exit code handling
  - Now uses helper function for cleaner code
  - Same functionality, better maintainability

- **Updated 6 unaudited scripts** to Phase 1 standards:
  - setup_ingress.sh: Added `set -euo pipefail`, common.sh, enable_debug_mode(), log functions
  - port_forward.sh: Added common.sh, enable_debug_mode(), log functions
  - minikube_service_url.sh: Added `set -euo pipefail`, common.sh, enable_debug_mode(), log functions
  - delete_local.sh: Added enable_debug_mode()
  - validate_workflow.sh: Added `set -euo pipefail`, enable_debug_mode(), fixed arithmetic expressions (19 instances)
  - generate_changelog.sh: Added note explaining standalone design (keeps own colors for markdown mode)

**Testing**:
- ✅ unit_tests.sh: 22 passed
- ✅ smoke_test.sh: 31 passed, 1 skipped
- ✅ readiness_test.sh --manual: Works correctly with run_pytest_optional()
- ✅ validate_repo_structure.sh: Passes with warnings
- ✅ validate_workflow.sh: Passes (arithmetic fixes working)

**Impact**:
- **Code Reuse**: Common patterns abstracted into reusable functions
- **Maintainability**: Less code duplication, easier to update
- **Consistency**: All 16 scripts now follow same standards
- **Robustness**: Better error handling and logging across all scripts
- **Completeness**: All scripts audited and updated

**Related**: See SCRIPT_REFACTORING_ANALYSIS.md for Phase 3 opportunities

---

### Documentation Updates

#### Root-Level TEST Reports Updated
- **TEST_COVERAGE_ANALYSIS.md**: Metrics updated to reflect probe refactoring
  - Integration: 11→12 files, 17→20 tests, ~2,100→~2,310 lines
  - Total: 24→25 files, 39→42 tests, 3,462→3,672 lines  
  - Educational: 59%→60% (23/39→25/42)
  - Added test_readiness_probe.py to inventory
  
- **TESTING_IMPROVEMENTS_SUMMARY.md**: Executive summary and evolution timeline
  - Added Phase 4: Probe Test Refactoring
  - Updated K8s checklist: split liveness (2) and readiness (3) tests
  - Added "Separation of Concerns" to quality metrics

#### Probe Test Refactoring - Separation of Concerns

**Context**: Liveness (/health) and readiness (/ready) probes serve different purposes and were mixed together.

**Added**:
- `test_readiness_probe.py`: 3 dedicated readiness tests
  - test_readiness_probe_configured
  - test_ready_replicas_match_desired  
  - test_all_running_pods_are_ready
- `scripts/readiness_test.sh`: Automation with 3 modes (default, --config, --manual)
- Makefile: `readiness-test`, `readiness-test-config`, `readiness-test-manual`

**Changed**:
- `test_liveness_probe.py`: Refactored to 2 liveness-only tests
- `test_deployment.py`: Use running_pods fixture (prevents stale pod issues)
- `utils.py`: Fixed get_running_pods() to exclude terminating pods
- Automation scripts: Updated messaging for "liveness & readiness"

**Documentation** (7 files updated):
- scripts/README.md, TESTING_WORKFLOWS.md, Makefile help
- docs/operations/probes/PROBES_GUIDE.md
- docs/testing/architecture/{TEST_ARCHITECTURE,TEST_REFACTORING}.md

**Fixed**:
- Race condition: terminating pods counted as "running" during graceful shutdown
- Solution: Filter pods with deletionTimestamp set
- Impact: Reliable pod counts after deployment updates

**Rationale**:
- Liveness = container restart decisions
- Readiness = traffic routing decisions  
- Separation improves clarity, discoverability, maintainability

---

#### Testing Workflows Documentation

**Added**:
- `TESTING_WORKFLOWS.md`: Complete workflow reference
  - All make targets documented
  - 16-step manual testing procedure
  - Test organization and markers

**Changed**:
- `test_health_endpoint.py`: Individual markers (@nodeport, @ingress, @educational)
- `health_endpoint_tests.sh`: kubectl patch for service restoration (prevents conflicts)
- `test_secret.py`: Use running_pods fixture
- `Makefile`: Removed duplicate nodeport step from test-full

**Fixed**:
- Educational test: flexible replica count (≥1 vs ==3)
- Ingress test: correct hostname (hello-flask.local)
- All test-full steps now passing

---

#### Documentation Consolidation

**Merged**:
- `TEST_COVERAGE_ANALYSIS.md` + `COMPREHENSIVE_TEST_COVERAGE_ANALYSIS.md` 
  → Single `TEST_COVERAGE_ANALYSIS.md` (1,612 lines)

**Streamlined**:
- `TESTING_IMPROVEMENTS_SUMMARY.md`: 583→347 lines (40% reduction)
  - Focus: evolution timeline, achievements, navigation map
  - References TEST_COVERAGE_ANALYSIS.md for details

**Removed**:
- COMPREHENSIVE_TEST_COVERAGE_ANALYSIS.md (merged)

---

## Archive: Auto-Generated Entries

<details>
<summary>Click to expand auto-generated changelog history</summary>

### 2025-11-22 13:36:32

**Added**:
- probes, test, debug and refactor all tests (ba77766)
- extra ingress tests for educational purposes (f1afc27)
- comprehensive K8s configuration testing (6c94e6f)

**Changed**:
- documentation after adding tests and refactoring (dd7070d)

**Other**:
- Enhance documentation and added extensive testing documentation (95fe46e)
- Extensive documentation refactoring and cleanup (d77e274)

---

### 2025-11-21 09:25:38

**Added**:
- comprehensive K8s configuration testing (ConfigMap, Secret) (6c94e6f)
- missing test scenarios (latency, 404) with pytest fixtures (166deca)

**Refactored**:
- config tests to use pytest fixtures and reduce duplication (46bd58a)

---

### 2025-11-16 18:52:55

**Documentation**:
- remove 11 historical files, rename 2, streamline 4 (17ce6a1, 8534f8a)

---

### 2025-11-14 (Multiple Entries)

**Added**:
- liveness test and documentation (1af4955, fa10aea, 5d4c838, 610837e)
- markers to run slow liveness tests manually (946f85b)
- liveness probe rules to manifest (bdf014f)
- consistent output to all test scripts (e0abf14)
- changelog generators (1c8441f)
- debug output for ingress verification (50db1b0)

**Changed**:
- script for ingress and port forwarding (13f3d7a)
- minikube-url comment improvements (1caf33d)

**Removed**:
- venv caching for robustness (2a6174c)
- EKS references (not used) (edbd93b, 2f7dbab, 59f2d4e, 1aae122, dfca020)
- unused file (5332a17)

**Other**:
- Extensive docs update after all tests succeeded (2c5f594)
- Refactoring to remove duplicate code (6858ed8, 64d8f09)
- Keep AIAD debugging logs for reference (ba6aa19)
- Debugging steps for ingress (27651bc)

---

### 2025-11-13

**Added**:
- ingress (9e6306a)

**Other**:
- need both url and hostname for tests (c75582d)

</details>

---

## Changelog Guidelines

**When to add manual entries**:
- Significant refactoring or architectural changes
- Breaking changes affecting developers
- New testing strategies or patterns
- Documentation consolidation efforts

**What to include**:
- Clear context and rationale
- Before/after comparisons
- Impact on workflows
- Related file changes

**Auto-generated entries**: Archived in collapsible section above. Run `scripts/generate_changelog.sh` to update.
