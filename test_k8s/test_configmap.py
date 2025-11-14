"""Test ConfigMap integration with pods."""
import pytest

from .utils import get_pods, exec_in_pod


def test_configmap_applied(pods):
    """Verify that ConfigMap environment variables are applied to pods."""
    assert len(pods) > 0, "No pods found to test ConfigMap"
    
    pod_name = pods[0]["metadata"]["name"]
    
    # Execute printenv in the pod to check APP_ENV variable
    result = exec_in_pod(pod_name, ["printenv", "APP_ENV"])
    env_value = result.stdout.strip()
    
    assert env_value == "local", \
        f"Expected APP_ENV='local', got '{env_value}'"
    
    print(f"✓ ConfigMap applied: APP_ENV={env_value}")
