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
	@echo "  build         - Build Docker image"
	@echo "  deploy        - Deploy to local cluster"
	@echo "  delete        - Delete local deployment"
	@echo "  test          - Run k8s tests"
	@echo "  unit-tests    - Run unit tests"
	@echo "  k8s-tests     - Run k8s integration tests"
	@echo "  liveness-test        - Run automated liveness probe configuration tests"
	@echo "  liveness-test-manual - Run manual behavioral tests (pod deletion, crash recovery)"
	@echo "  liveness-test-config - Run only liveness probe configuration check"
	@echo "  test-all      - Run all tests"
	@echo "  smoke-test    - Run smoke tests"
	@echo "  port-forward  - Forward service port to localhost"
	@echo "  minikube-url  - Get service URL and access methods"
	@echo "  changelog     - Generate changelog from all commits"
	@echo "  changelog-since TAG=v1.0.0 - Generate changelog since a specific tag"
	@echo "  changelog-range FROM=v1.0.0 TO=v2.0.0 - Generate changelog between tags"
	@echo "  changelog-dev - Append auto-generated changelog to CHANGELOG_DEV.md"
	@echo "  changelog-dev-since TAG=v1.0.0 - Append changelog since tag to CHANGELOG_DEV.md"
	@echo "  full-deploy   - Complete build, deploy, and smoke test"
	@echo "  help          - Show this help message"
