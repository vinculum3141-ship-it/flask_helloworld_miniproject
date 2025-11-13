import subprocess, json

def test_pods_running():
    """Check that all pods are in Running state."""
    result = subprocess.run(
        ["minikube", "kubectl", "--", "get", "pods", "-o", "json"],
        capture_output=True, text=True
    )
    pods = json.loads(result.stdout)
    for pod in pods["items"]:
        status = pod["status"]["phase"]
        assert status == "Running", f"Pod {pod['metadata']['name']} not running (status={status})"
