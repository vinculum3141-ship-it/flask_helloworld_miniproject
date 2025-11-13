build:
	@bash scripts/build_image.sh

deploy:
	@bash scripts/deploy_local.sh

delete:
	@bash scripts/delete_local.sh

# Additional script targets
k8s-tests:
	@bash scripts/k8s_tests.sh

minikube-url:
	@bash scripts/minikube_service_url.sh

port-forward:
	@bash scripts/port_forward.sh

smoke-test:
	@bash scripts/smoke_test.sh

unit-tests:
	@bash scripts/unit_tests.sh

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
	@echo "  test-all      - Run all tests"
	@echo "  smoke-test    - Run smoke tests"
	@echo "  port-forward  - Forward service port to localhost"
	@echo "  minikube-url  - Get minikube service URL"
	@echo "  full-deploy   - Complete build, deploy, and smoke test"
	@echo "  help          - Show this help message"
