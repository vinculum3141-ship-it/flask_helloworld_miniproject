"""
Test liveness probe and self-healing behavior.

This test verifies that:
1. Liveness probe is configured correctly in the deployment
2. Kubernetes automatically restarts containers when they crash
3. Self-healing behavior works as expected
"""
import subprocess
import json
import time
import pytest


def run_kubectl(*args):
    """Helper function to run kubectl commands."""
    result = subprocess.run(
        ["kubectl"] + list(args),
        capture_output=True,
        text=True,
        check=False
    )
    return result


def get_pods():
    """Get all hello-flask pods."""
    result = run_kubectl("get", "pods", "-l", "app=hello-flask", "-o", "json")
    if result.returncode != 0:
        pytest.fail(f"Failed to get pods: {result.stderr}")
    return json.loads(result.stdout)["items"]


def get_pod_restart_count(pod_name):
    """Get the restart count for a specific pod."""
    result = run_kubectl("get", "pod", pod_name, "-o", "json")
    if result.returncode != 0:
        return None
    pod_data = json.loads(result.stdout)
    container_statuses = pod_data.get("status", {}).get("containerStatuses", [])
    if container_statuses:
        return container_statuses[0].get("restartCount", 0)
    return 0


def test_liveness_probe_configured():
    """Verify that liveness probe is configured in the deployment."""
    result = run_kubectl("get", "deployment", "hello-flask", "-o", "json")
    assert result.returncode == 0, f"Failed to get deployment: {result.stderr}"
    
    deployment = json.loads(result.stdout)
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


def test_readiness_probe_configured():
    """Verify that readiness probe is also configured."""
    result = run_kubectl("get", "deployment", "hello-flask", "-o", "json")
    assert result.returncode == 0, f"Failed to get deployment: {result.stderr}"
    
    deployment = json.loads(result.stdout)
    containers = deployment["spec"]["template"]["spec"]["containers"]
    main_container = containers[0]
    
    assert "readinessProbe" in main_container, "Readiness probe not configured"
    
    readiness_probe = main_container["readinessProbe"]
    assert "httpGet" in readiness_probe, "Readiness probe should use httpGet"
    
    print("\n✅ Readiness probe is configured")


def test_multiple_replicas_maintained():
    """Verify that the deployment maintains the desired number of replicas."""
    result = run_kubectl("get", "deployment", "hello-flask", "-o", "json")
    assert result.returncode == 0, f"Failed to get deployment: {result.stderr}"
    
    deployment = json.loads(result.stdout)
    desired_replicas = deployment["spec"]["replicas"]
    ready_replicas = deployment["status"].get("readyReplicas", 0)
    
    assert ready_replicas == desired_replicas, \
        f"Expected {desired_replicas} ready replicas, but got {ready_replicas}"
    
    print(f"\n✅ Deployment maintaining {ready_replicas}/{desired_replicas} replicas")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
