# Documentation Index

This directory contains comprehensive documentation for the Flask Hello World Mini Project.

## 📁 Directory Structure

```
docs/
├── README.md (this file)         # Documentation index
├── testing/                       # Test suite documentation
│   ├── TEST_ARCHITECTURE.md      # Test suite architecture and design
│   ├── TEST_REFACTORING.md       # Refactoring summary and changes
│   └── README_UPDATES.md         # README update history
├── scripts/                       # Bash script documentation
│   └── SCRIPT_UPDATES.md         # Script changes and updates
├── CHANGELOG_GUIDE.md            # Changelog maintenance guide
├── CI_CD_FIX_SUMMARY.md          # CI/CD pipeline fixes
├── DEBUGGING_CI_CD.md            # CI/CD debugging guide
├── INGRESS_404_EXPLAINED.md      # Ingress troubleshooting
├── MINIKUBE_SERVICE_URL_FIX.md   # Minikube service access
└── README_CURL_FIX.md            # cURL command fixes
```

## 📚 Documentation Categories

### Testing Documentation
Located in `docs/testing/`

- **[TEST_ARCHITECTURE.md](testing/TEST_ARCHITECTURE.md)** - Complete test suite architecture, including:
  - Shared utilities overview
  - Pytest fixtures reference
  - Custom marker documentation
  - Test organization principles

- **[TEST_REFACTORING.md](testing/TEST_REFACTORING.md)** - Refactoring summary covering:
  - Changes made to test files
  - Benefits and improvements
  - Migration guide
  - Best practices

- **[README_UPDATES.md](testing/README_UPDATES.md)** - README update history

### Scripts Documentation
Located in `docs/scripts/`

- **[SCRIPT_UPDATES.md](scripts/SCRIPT_UPDATES.md)** - Bash script changes including:
  - Updated scripts overview
  - Pytest marker integration
  - Usage examples
  - Migration notes

### CI/CD & Operations
Located in `docs/` (root)

- **[CI_CD_FIX_SUMMARY.md](CI_CD_FIX_SUMMARY.md)** - Summary of CI/CD pipeline fixes
- **[DEBUGGING_CI_CD.md](DEBUGGING_CI_CD.md)** - Guide for debugging CI/CD issues
- **[CHANGELOG_GUIDE.md](CHANGELOG_GUIDE.md)** - How to maintain changelogs
- **[DOCUMENTATION_REORGANIZATION.md](DOCUMENTATION_REORGANIZATION.md)** - Documentation structure guide

### Troubleshooting Guides
Located in `docs/` (root)

- **[INGRESS_404_EXPLAINED.md](INGRESS_404_EXPLAINED.md)** - Ingress 404 error troubleshooting
- **[MINIKUBE_SERVICE_URL_FIX.md](MINIKUBE_SERVICE_URL_FIX.md)** - Minikube service access issues
- **[README_CURL_FIX.md](README_CURL_FIX.md)** - cURL command troubleshooting

## 🔍 Quick Links

### Getting Started
- [Main README](../README.md) - Project overview and setup
- [Test README](../test_k8s/README.md) - Test usage guide

### For Developers
- [Test Architecture](testing/TEST_ARCHITECTURE.md) - Understand the test suite
- [Test Refactoring](testing/TEST_REFACTORING.md) - Recent improvements
- [Script Updates](scripts/SCRIPT_UPDATES.md) - Bash script changes

### For Operations
- [CI/CD Debugging](DEBUGGING_CI_CD.md) - Troubleshoot pipeline issues
- [Ingress Guide](INGRESS_404_EXPLAINED.md) - Fix ingress problems
- [Minikube Guide](MINIKUBE_SERVICE_URL_FIX.md) - Service access issues

## 📝 Contributing

When adding new documentation:
- Place test-related docs in `docs/testing/`
- Place script-related docs in `docs/scripts/`
- Place general operational docs in `docs/` root
- Update this index file
- Follow Markdown best practices
