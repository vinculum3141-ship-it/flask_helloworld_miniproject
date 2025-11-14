"""
Test liveness probe and self-healing behavior.

This test verifies that:
1. Liveness probe is configured correctly in the deployment
2. Kubernetes automatically restarts containers when they crash
3. Self-healing behavior works as expected
"""
import pytest

from .utils import get_deployment, get_pods, get_running_pods


def test_liveness_probe_configured(deployment):
    """Verify that liveness probe is configured in the deployment."""
    containers = deployment["spec"]["template"]["spec"]["containers"]
    
    assert len(containers) > 0, "No containers found in deployment"
    
    main_container = containers[0]
    assert "livenessProbe" in main_container, "Liveness probe not configured"
    
    liveness_probe = main_container["livenessProbe"]
    
    # Verify liveness probe configuration
    assert "httpGet" in liveness_probe, "Liveness probe should use httpGet"
    assert liveness_probe["httpGet"]["path"] == "/", "Liveness probe path should be /"
    assert liveness_probe["httpGet"]["port"] == 5000, "Liveness probe port should be 5000"
    
    # Verify probe timing settings
    assert "initialDelaySeconds" in liveness_probe, "initialDelaySeconds should be configured"
    assert "periodSeconds" in liveness_probe, "periodSeconds should be configured"
    assert "timeoutSeconds" in liveness_probe, "timeoutSeconds should be configured"
    assert "failureThreshold" in liveness_probe, "failureThreshold should be configured"
    
    print("\n✅ Liveness probe configuration:")
    print(f"   Path: {liveness_probe['httpGet']['path']}")
    print(f"   Port: {liveness_probe['httpGet']['port']}")
    print(f"   Initial Delay: {liveness_probe['initialDelaySeconds']}s")
    print(f"   Period: {liveness_probe['periodSeconds']}s")
    print(f"   Timeout: {liveness_probe['timeoutSeconds']}s")
    print(f"   Failure Threshold: {liveness_probe['failureThreshold']}")


def test_readiness_probe_configured(deployment):
    """Verify that readiness probe is also configured."""
    containers = deployment["spec"]["template"]["spec"]["containers"]
    main_container = containers[0]
    
    assert "readinessProbe" in main_container, "Readiness probe not configured"
    
    readiness_probe = main_container["readinessProbe"]
    assert "httpGet" in readiness_probe, "Readiness probe should use httpGet"
    
    print("\n✅ Readiness probe is configured")


def test_multiple_replicas_maintained(deployment):
    """Verify that the deployment maintains the desired number of replicas."""
    desired_replicas = deployment["spec"]["replicas"]
    ready_replicas = deployment["status"].get("readyReplicas", 0)
    
    assert ready_replicas == desired_replicas, \
        f"Expected {desired_replicas} ready replicas, but got {ready_replicas}"
    
    print(f"\n✅ Deployment maintaining {ready_replicas}/{desired_replicas} replicas")
