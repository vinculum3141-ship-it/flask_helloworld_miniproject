build:
	@bash scripts/build_image.sh

deploy:
	@bash scripts/deploy_local.sh

delete:
	@bash scripts/delete_local.sh

# Additional script targets
k8s-tests:
	@bash scripts/k8s_tests.sh

liveness-test:
	@bash scripts/liveness_test.sh

liveness-test-manual:
	@bash scripts/liveness_test.sh --manual

liveness-test-config:
	@bash scripts/liveness_test.sh --config

minikube-url:
	@bash scripts/minikube_service_url.sh

port-forward:
	@bash scripts/port_forward.sh

smoke-test:
	@bash scripts/smoke_test.sh

unit-tests:
	@bash scripts/unit_tests.sh

# Educational tests (Ingress concepts)
educational-tests:
	@echo "Running educational Ingress tests..."
	@pytest test_k8s/ -m educational -v -s

# All Ingress tests (basic + educational)
ingress-tests:
	@echo "Running all Ingress tests (basic + educational)..."
	@pytest test_k8s/ -m ingress -v -s

# Validation targets
validate-repo:
	@bash scripts/validate_repo_structure.sh

validate-workflow:
	@bash scripts/validate_workflow.sh

validate-all: validate-repo validate-workflow

# Changelog generation
changelog:
	@bash scripts/generate_changelog.sh

changelog-since:
	@bash scripts/generate_changelog.sh $(TAG)

changelog-range:
	@bash scripts/generate_changelog.sh $(FROM) $(TO)

changelog-dev:
	@echo "" >> CHANGELOG_DEV.md
	@echo "---" >> CHANGELOG_DEV.md
	@echo "" >> CHANGELOG_DEV.md
	@echo "## Auto-generated Entry" >> CHANGELOG_DEV.md
	@echo "" >> CHANGELOG_DEV.md
	@echo "**Generated:** $$(date '+%Y-%m-%d %H:%M:%S')" >> CHANGELOG_DEV.md
	@echo "" >> CHANGELOG_DEV.md
	@bash scripts/generate_changelog.sh $(if $(TAG),$(TAG)) $(if $(TO),$(TO)) --markdown-only >> CHANGELOG_DEV.md
	@echo "" >> CHANGELOG_DEV.md
	@echo "✅ Changelog appended to CHANGELOG_DEV.md"

changelog-dev-since:
	@echo "" >> CHANGELOG_DEV.md
	@echo "---" >> CHANGELOG_DEV.md
	@echo "" >> CHANGELOG_DEV.md
	@echo "## Auto-generated Entry" >> CHANGELOG_DEV.md
	@echo "" >> CHANGELOG_DEV.md
	@echo "**Generated:** $$(date '+%Y-%m-%d %H:%M:%S')" >> CHANGELOG_DEV.md
	@echo "" >> CHANGELOG_DEV.md
	@echo "**Since:** $(TAG)" >> CHANGELOG_DEV.md
	@echo "" >> CHANGELOG_DEV.md
	@bash scripts/generate_changelog.sh $(TAG) --markdown-only >> CHANGELOG_DEV.md
	@echo "" >> CHANGELOG_DEV.md
	@echo "✅ Changelog appended to CHANGELOG_DEV.md"

# Run all tests (unit + k8s)
test-all: unit-tests k8s-tests

# Complete workflow
full-deploy: build deploy smoke-test

# Help target to show available commands
help:
	@echo "Available targets:"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  build         - Build Docker image"
	@echo "  deploy        - Deploy to local cluster"
	@echo "  delete        - Delete local deployment"
	@echo "  full-deploy   - Build, deploy, and run smoke tests"
	@echo ""
	@echo "Testing:"
	@echo "  unit-tests           - Run unit tests"
	@echo "  k8s-tests            - Run k8s integration tests (excludes manual & educational)"
	@echo "  educational-tests    - Run educational Ingress tests (hostname routing, consistency, load balancing)"
	@echo "  ingress-tests        - Run all Ingress tests (basic + educational)"
	@echo "  smoke-test           - Run smoke tests (quick validation)"
	@echo "  test-all             - Run all automated tests (unit + k8s)"
	@echo ""
	@echo "Liveness Probe Tests:"
	@echo "  liveness-test        - Run automated liveness probe configuration tests"
	@echo "  liveness-test-manual - Run manual behavioral tests (pod deletion, crash recovery)"
	@echo "  liveness-test-config - Run only liveness probe configuration check"
	@echo ""
	@echo "Utilities:"
	@echo "  port-forward  - Forward service port to localhost"
	@echo "  minikube-url  - Get service URL and access methods"
	@echo ""
	@echo "Validation:"
	@echo "  validate-repo     - Validate repository structure"
	@echo "  validate-workflow - Validate GitHub Actions workflow configuration"
	@echo "  validate-all      - Run all validation checks"
	@echo "  changelog     - Generate changelog from all commits"
	@echo "  changelog-since TAG=v1.0.0 - Generate changelog since a specific tag"
	@echo "  changelog-range FROM=v1.0.0 TO=v2.0.0 - Generate changelog between tags"
	@echo "  changelog-dev - Append auto-generated changelog to CHANGELOG_DEV.md"
	@echo "  changelog-dev-since TAG=v1.0.0 - Append changelog since tag to CHANGELOG_DEV.md"
	@echo "  full-deploy   - Complete build, deploy, and smoke test"
	@echo "  help          - Show this help message"
