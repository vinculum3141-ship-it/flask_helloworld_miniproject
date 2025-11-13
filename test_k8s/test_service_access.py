import subprocess
import requests
import time
import json

def get_service_type():
    """Determine if service is NodePort or ClusterIP."""
    result = subprocess.run(
        ["kubectl", "get", "svc", "hello-flask", "-o", "json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    
    svc_data = json.loads(result.stdout)
    return svc_data.get("spec", {}).get("type", "ClusterIP")

def get_nodeport_url():
    """Get service URL for NodePort service type."""
    url = ""
    for i in range(5):
        proc = subprocess.run(
            ["minikube", "service", "hello-flask", "--url"],
            capture_output=True, text=True
        )
        url = proc.stdout.strip()
        if url:
            break
        time.sleep(1)
    return url

def get_ingress_url():
    """Get URL from Ingress resource."""
    # Check if ingress exists
    result = subprocess.run(
        ["kubectl", "get", "ingress", "hello-flask-ingress", "-o", "json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    
    ingress_data = json.loads(result.stdout)
    rules = ingress_data.get("spec", {}).get("rules", [])
    if not rules:
        return None
    
    host = rules[0].get("host", "hello-flask.local")
    return f"http://{host}"

def test_service_reachable():
    """Ensure the exposed service URL is responding.
    
    This test supports both NodePort and ClusterIP (with Ingress) service types.
    - For NodePort: Uses 'minikube service hello-flask --url'
    - For ClusterIP with Ingress: Uses the Ingress host (e.g., http://hello-flask.local)
    """
    service_type = get_service_type()
    assert service_type, "Could not determine service type. Is the service deployed?"
    
    print(f"Detected service type: {service_type}")
    
    if service_type == "NodePort":
        # Test NodePort access
        url = get_nodeport_url()
        assert url, (
            "minikube returned an empty URL for service 'hello-flask'. "
            "Is the service deployed with type NodePort?"
        )
        assert url.startswith(("http://", "https://")), f"Service URL does not include scheme: {url!r}"
        
    elif service_type == "ClusterIP":
        # Test Ingress access
        url = get_ingress_url()
        assert url, (
            "No Ingress found for service 'hello-flask'. "
            "For ClusterIP services, you need to deploy an Ingress resource. "
            "Either deploy k8s/ingress.yaml or change service type to NodePort."
        )
        print(f"Testing via Ingress: {url}")
        
    else:
        raise AssertionError(f"Unsupported service type: {service_type}")
    
    # Test the URL
    try:
        resp = requests.get(url, timeout=5)
        assert resp.status_code == 200, f"Unexpected status {resp.status_code} from {url}"
        assert "Hello" in resp.text, f"Expected 'Hello' in response from {url}"
        print(f"✓ Service is reachable at {url}")
    except requests.exceptions.RequestException as e:
        raise AssertionError(
            f"Failed to reach service at {url}. "
            f"Error: {e}. "
            f"If using Ingress, ensure: 1) Ingress controller is running, "
            f"2) /etc/hosts is configured, 3) Ingress resource is deployed."
        )
