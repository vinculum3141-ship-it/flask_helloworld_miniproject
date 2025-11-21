# Documentation Index

This directory contains comprehensive documentation for the Flask Hello World Mini Project.

## 📁 Directory Structure

```
docs/
├── README.md (this file)         # Documentation index
├── testing/                       # Test suite documentation
│   ├── TEST_ARCHITECTURE.md      # Test suite architecture and design
│   ├── TEST_REFACTORING.md       # Refactoring summary and changes
│   └── SCRIPT_INTEGRATION.md     # Script integration with pytest markers
├── EDUCATIONAL_TESTS.md          # Educational Ingress tests guide
├── EDUCATIONAL_TESTS_SUMMARY.md  # Educational tests implementation summary
├── EDUCATIONAL_TESTS_QUICKREF.md # Educational tests quick reference
├── EDUCATIONAL_TESTS_CI_CD.md    # Educational tests in CI/CD configuration
├── CHANGELOG_GUIDE.md            # Changelog maintenance guide
├── INGRESS_CI_CD_TROUBLESHOOTING.md  # CI/CD and Ingress troubleshooting
├── CI_CD_GUIDE.md                # CI/CD pipeline guide
├── INGRESS_404_EXPLAINED.md      # Ingress troubleshooting
├── DEVELOPMENT_WORKFLOW.md       # Development workflow and best practices
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

- **[SCRIPT_INTEGRATION.md](testing/SCRIPT_INTEGRATION.md)** - Script integration with pytest markers including:
  - Script test execution behavior
  - Pytest marker reference
  - Running tests manually
  - Related documentation links

- **[EDUCATIONAL_TESTS.md](EDUCATIONAL_TESTS.md)** - Educational Ingress tests including:
  - Hostname-based routing demonstration
  - Response consistency validation
  - Load balancing observation
  - How to run and extend educational tests

- **[EDUCATIONAL_TESTS_SUMMARY.md](EDUCATIONAL_TESTS_SUMMARY.md)** - Implementation summary of educational tests

- **[EDUCATIONAL_TESTS_QUICKREF.md](EDUCATIONAL_TESTS_QUICKREF.md)** - Quick reference for running educational tests

- **[EDUCATIONAL_TESTS_CI_CD.md](EDUCATIONAL_TESTS_CI_CD.md)** - CI/CD configuration for educational tests including:
  - Current behavior (included by default)
  - Test execution breakdown
  - How to exclude if needed
  - Timing and recommendations

### CI/CD & Operations
Located in `docs/` (root)

- **[CI_CD_GUIDE.md](CI_CD_GUIDE.md)** - Complete CI/CD pipeline reference including:
  - Workflow triggers and stages
  - Features checklist and capabilities
  - GitHub CLI usage and examples
  - Manual testing and validation
  - Troubleshooting guide
- **[INGRESS_CI_CD_TROUBLESHOOTING.md](INGRESS_CI_CD_TROUBLESHOOTING.md)** - CI/CD and Ingress troubleshooting including:
  - Ingress Host header routing in CI/CD
  - Multiple solution approaches
  - Step-by-step debugging guide
  - Common issues and solutions
- **[CHANGELOG_GUIDE.md](CHANGELOG_GUIDE.md)** - How to maintain changelogs

### Troubleshooting Guides
Located in `docs/` (root)

- **[INGRESS_404_EXPLAINED.md](INGRESS_404_EXPLAINED.md)** - Ingress 404 error troubleshooting

## 🔍 Quick Links

### Getting Started
- [Main README](../README.md) - Project overview and setup
- [Test README](../test_k8s/README.md) - Test usage guide

### For Developers
- [Development Workflow](DEVELOPMENT_WORKFLOW.md) - Pre-push validation and best practices
- [Test Architecture](testing/TEST_ARCHITECTURE.md) - Understand the test suite
- [Test Refactoring](testing/TEST_REFACTORING.md) - Recent improvements
- [Script Integration](testing/SCRIPT_INTEGRATION.md) - Script integration with pytest markers
- [Educational Tests](EDUCATIONAL_TESTS.md) - Learn Ingress concepts through hands-on testing

### For Operations
- [Development Workflow](DEVELOPMENT_WORKFLOW.md) - Pre-push validation scripts
- [CI/CD Guide](CI_CD_GUIDE.md) - Complete pipeline reference
- [CI/CD Troubleshooting](INGRESS_CI_CD_TROUBLESHOOTING.md) - Ingress and pipeline debugging
- [Ingress Guide](INGRESS_404_EXPLAINED.md) - Fix ingress problems
- [Scripts Guide](../scripts/README.md) - Automation scripts including service access

## 📝 Contributing

When adding new documentation:
- **Test documentation** goes in `docs/testing/` (architecture, design, best practices)
- **Usage guides** stay with the code (e.g., `test_k8s/README.md` for test usage)
- **Operational docs** go in `docs/` root (troubleshooting, guides, workflows)
- **Update this index file** when adding new documentation
- **Follow Markdown best practices** (clear headings, code blocks, links)

### Documentation Organization Principles

- ✅ **Separation of Concerns**: Group related documentation together
- ✅ **Clear Naming**: Use descriptive filenames (e.g., `TEST_ARCHITECTURE.md`, `CI_CD_GUIDE.md`)
- ✅ **Discoverability**: Maintain this index and cross-reference related docs
- ✅ **Keep Usage with Code**: User-facing guides stay near the code they document
- ✅ **Centralize Architecture**: Design and architecture docs belong in `docs/`
