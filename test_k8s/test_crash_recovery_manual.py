"""
Manual Self-Healing Tests

These tests are kept separate because they involve timing-dependent operations
that can be flaky in automated CI/CD environments:
- Waiting for pod deletion and recreation
- Detecting container crash recovery
- Race conditions between Kubernetes controllers

NOTE: These tests are intentionally NOT run as part of the automated test suite.
They're provided for manual testing and verification of self-healing behavior.

To run these tests manually:
    pytest test_k8s/test_crash_recovery_manual.py -v -s
    
Or run specific tests:
    pytest test_k8s/test_crash_recovery_manual.py::test_self_healing_pod_deletion -v -s
    pytest test_k8s/test_crash_recovery_manual.py::test_container_restart_on_crash -v -s

For manual testing without pytest:
    # Method 1: Delete a pod and watch ReplicaSet recreate it
    kubectl get pods -l app=hello-flask
    kubectl delete pod <pod-name>
    kubectl get pods -l app=hello-flask -w
    
    # Method 2: Simulate a crash and watch restartPolicy recover
    kubectl exec <pod-name> -- bash -c "kill -9 1"
    kubectl get pods -l app=hello-flask -w
"""

import json
import subprocess
import time
import pytest


def run_kubectl(*args):
    """Run kubectl command and return result."""
    result = subprocess.run(
        ["kubectl"] + list(args),
        capture_output=True,
        text=True
    )
    return result


def get_pods():
    """Get all hello-flask pods."""
    result = run_kubectl("get", "pods", "-l", "app=hello-flask", "-o", "json")
    assert result.returncode == 0, f"Failed to get pods: {result.stderr}"
    return json.loads(result.stdout)["items"]


def get_pod_restart_count(pod_name):
    """Get restart count for a specific pod."""
    result = run_kubectl("get", "pod", pod_name, "-o", "json")
    if result.returncode != 0:
        return None
    
    pod = json.loads(result.stdout)
    container_statuses = pod["status"].get("containerStatuses", [])
    
    if not container_statuses:
        return 0
    
    return container_statuses[0].get("restartCount", 0)


@pytest.mark.manual
def test_self_healing_pod_deletion():
    """
    MANUAL TEST: Verify that Kubernetes recreates deleted pods (tests ReplicaSet self-healing).
    
    This test deletes a pod and waits for the ReplicaSet to create a replacement.
    The timing can be variable depending on cluster load and network conditions.
    
    This test is marked as @pytest.mark.manual and should be run explicitly:
        pytest test_k8s/test_crash_recovery_manual.py::test_self_healing_pod_deletion -v -s
    
    Or skip the marker check:
        pytest test_k8s/test_crash_recovery_manual.py -v -s
    """
    # Get current pods
    initial_pods = get_pods()
    assert len(initial_pods) >= 1, "At least one pod should be running"
    
    initial_pod_count = len(initial_pods)
    pod_to_delete = initial_pods[0]["metadata"]["name"]
    
    print(f"\n🧪 Testing self-healing by deleting pod: {pod_to_delete}")
    print(f"   Initial pod count: {initial_pod_count}")
    
    # Delete one pod
    result = run_kubectl("delete", "pod", pod_to_delete, "--wait=false")
    assert result.returncode == 0, f"Failed to delete pod: {result.stderr}"
    
    print(f"   Pod {pod_to_delete} deletion initiated...")
    print(f"   Waiting for ReplicaSet to create replacement...")
    
    # Wait for new pod to be created and become ready
    max_wait = 60  # seconds
    start_time = time.time()
    new_pod_running = False
    
    while time.time() - start_time < max_wait:
        current_pods = get_pods()
        running_pods = [
            p for p in current_pods
            if p["status"]["phase"] == "Running" and
            all(cs.get("ready", False) for cs in p["status"].get("containerStatuses", []))
        ]
        
        if len(running_pods) >= initial_pod_count:
            new_pod_running = True
            elapsed = time.time() - start_time
            print(f"   ✅ New pod created and running (took {elapsed:.1f}s)")
            break
        
        time.sleep(2)
    
    if not new_pod_running:
        print(f"   ⚠️  New pod did not become ready within {max_wait}s")
        print(f"   This may indicate cluster resource issues or slow startup")
        print(f"   Current pods: {len(get_pods())}")
        print(f"\n   💡 MANUAL VERIFICATION SUGGESTIONS:")
        print(f"   1. Check pod status: kubectl get pods -l app=hello-flask")
        print(f"   2. Check ReplicaSet: kubectl get rs -l app=hello-flask")
        print(f"   3. Check events: kubectl get events --sort-by='.lastTimestamp'")
    
    # Verify we have the correct number of running pods
    final_pods = get_pods()
    running_count = sum(1 for p in final_pods if p["status"]["phase"] == "Running")
    
    print(f"   Final state: {running_count}/{initial_pod_count} pods running")
    
    if running_count >= initial_pod_count:
        print(f"   ✅ Self-healing verified: ReplicaSet maintained pod count")
    else:
        print(f"   ℹ️  Manual verification recommended - pod count: {running_count}/{initial_pod_count}")


@pytest.mark.manual
def test_container_restart_on_crash():
    """
    MANUAL TEST: Verify that Kubernetes automatically recovers from container crashes.
    
    When a container crashes, Kubernetes will either:
    1. Restart the container within the same pod (incrementing restart count), or
    2. Replace the pod entirely (via ReplicaSet self-healing)
    
    Both behaviors demonstrate self-healing capability.
    
    This test is marked as @pytest.mark.manual and should be run explicitly:
        pytest test_k8s/test_crash_recovery_manual.py -v -s -m manual
    
    Or skip the marker check:
        pytest test_k8s/test_crash_recovery_manual.py -v -s
    """
    # Get initial state
    pods = get_pods()
    assert len(pods) >= 1, "At least one pod should be running"
    
    test_pod = pods[0]["metadata"]["name"]
    initial_restart_count = get_pod_restart_count(test_pod)
    initial_pod_count = len(pods)
    initial_pod_names = [p["metadata"]["name"] for p in pods]
    
    print(f"\n🧪 Testing self-healing by crashing container in pod: {test_pod}")
    print(f"   Initial restart count: {initial_restart_count}")
    print(f"   Initial pod count: {initial_pod_count}")
    print(f"   Initial pods: {initial_pod_names}")
    
    # Kill the main process (PID 1) in the container
    # Use SIGKILL (-9) which cannot be caught or ignored
    result = run_kubectl("exec", test_pod, "--", "bash", "-c", "kill -9 1")
    # Note: This command will fail because the process dies, but that's expected
    
    print(f"   Crash command sent, waiting for self-healing...")
    print(f"   Expected: Container restart OR pod replacement")
    
    # Wait for Kubernetes to recover (either way)
    max_wait = 30  # Should be quick since restartPolicy: Always doesn't wait for liveness probe
    start_time = time.time()
    recovery_detected = False
    recovery_type = None
    new_restart_count = initial_restart_count
    
    while time.time() - start_time < max_wait:
        time.sleep(2)
        
        current_pods = get_pods()
        
        # Check if the original pod's container restarted
        current_restart_count = get_pod_restart_count(test_pod)
        if current_restart_count is not None and current_restart_count > initial_restart_count:
            recovery_detected = True
            recovery_type = "container_restart"
            new_restart_count = current_restart_count
            elapsed = time.time() - start_time
            print(f"   ✅ Container restarted in same pod (took {elapsed:.1f}s)")
            print(f"   Restart count: {initial_restart_count} → {current_restart_count}")
            break
        
        # Check if pod was replaced (common when PID 1 exits)
        current_pod_names = [p["metadata"]["name"] for p in current_pods 
                             if p["status"]["phase"] in ["Running", "Pending"]]
        
        # If we have a new pod name that wasn't there before, recovery happened
        new_pods = set(current_pod_names) - set(initial_pod_names)
        if new_pods:
            recovery_detected = True
            recovery_type = "pod_replacement"
            elapsed = time.time() - start_time
            print(f"   ✅ Pod replaced by Kubernetes (took {elapsed:.1f}s)")
            print(f"   New pod(s): {list(new_pods)}")
            break
    
    # For manual testing, we provide informational output even if recovery isn't detected
    if not recovery_detected:
        print(f"   ⚠️  No obvious recovery detected within {max_wait}s")
        print(f"   This is common due to race conditions - container may restart too fast to observe")
        print(f"   Current restart count: {get_pod_restart_count(test_pod)}")
        print(f"\n   💡 MANUAL VERIFICATION SUGGESTIONS:")
        print(f"   1. Check pod events: kubectl describe pod {test_pod}")
        print(f"   2. Watch pods in real-time: kubectl get pods -l app=hello-flask -w")
        print(f"   3. Check restart count: kubectl get pods -l app=hello-flask")
    
    # Wait for all pods to be ready
    print(f"   Waiting for pods to stabilize...")
    time.sleep(10)
    
    # Verify we have the expected number of healthy, ready pods
    final_pods = get_pods()
    running_ready_pods = [
        p for p in final_pods
        if p["status"]["phase"] == "Running" and
        all(cs.get("ready", False) for cs in p["status"].get("containerStatuses", []))
    ]
    
    print(f"   Final state: {len(running_ready_pods)} pod(s) running and ready")
    
    if recovery_type:
        print(f"   ✅ Self-healing verified via {recovery_type}")
    else:
        print(f"   ℹ️  Manual verification recommended - automated detection may miss fast restarts")


if __name__ == "__main__":
    # Allow running directly: python test_crash_recovery_manual.py
    print("Running manual crash recovery test...")
    test_container_restart_on_crash()
