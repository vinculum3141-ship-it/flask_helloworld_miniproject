"""Test deployment and pod status."""
import pytest

from .utils import get_pods


def test_pods_running(pods):
    """Check that all pods are in Running state."""
    assert len(pods) > 0, "No pods found"
    
    for pod in pods:
        pod_name = pod["metadata"]["name"]
        status = pod["status"]["phase"]
        
        assert status == "Running", \
            f"Pod {pod_name} not running (status={status})"
    
    print(f"✓ All {len(pods)} pod(s) are running")
